import os
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from anthropic import AsyncAnthropic, APIError
from dotenv import load_dotenv

# Enviroment.

ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
HAPPY_MODEL = os.getenv("HAPPY_MODEL", "claude-sonnet-5")

if not ANTHROPIC_API_KEY:
    raise ValueError(
        "ANTHROPIC_API_KEY is missing from the .env file."
    )

client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)


# Personality and responsibilites.

PROMPT_FILE = Path(__file__).resolve().parent / "happy_prompt.txt"


def load_system_prompt():
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(
            "happy_prompt.txt is missing. "
            "Create it in the same folder as ai.py."
        )

    with open(PROMPT_FILE, "r", encoding="utf-8") as file:
        prompt = file.read().strip()

    if not prompt:
        raise ValueError("happy_prompt.txt is empty.")

    return prompt


HAPPY_SYSTEM_PROMPT = load_system_prompt()

# Response.

def extract_answer_and_sources(response):
    """
    Extract Happy's written answer and cited web sources
    from the Anthropic response.
    """

    text_parts = []
    sources = []
    seen_urls = set()

    for block in response.content:
        if block.type != "text":
            continue

        text_parts.append(block.text)

        citations = getattr(block, "citations", None) or []

        for citation in citations:
            url = getattr(citation, "url", None)
            title = getattr(citation, "title", None) or "Source"

            if url and url not in seen_urls:
                seen_urls.add(url)
                sources.append(f"- [{title}]({url})")

    answer = "".join(text_parts).strip()

    if sources:
        answer += "\n\n**Sources**\n"
        answer += "\n".join(sources)

    return answer


# Main ask definition.

async def ask_happy(user_message, notes=None):
    """
    Send user's message to Happy and return Happy's response.

    Saved notes are supplied as private context. Happy may use relevant
    information from them, but should not list or expose the notes unless
    user directly asks to see them.
    """

    current_date = datetime.now(
        ZoneInfo("America/Los_Angeles")
    ).strftime("%A, %B %d, %Y")

    if notes:
        if isinstance(notes, str):
            notes_text = notes
        else:
            notes_text = json.dumps(
                notes,
                indent=2,
                ensure_ascii=False,
                default=str
            )
    else:
        notes_text = "No saved notes are available."

    messages = [
        {
            "role": "user",
            "content": (
                f"Today's date in user's timezone is "
                f"{current_date}.\n\n"
                "The following saved notes are private context. "
                "Use only notes relevant to the request. Do not list, "
                "quote, or expose them unless user explicitly asks.\n\n"
                f"Saved notes:\n{notes_text}\n\n"
                f"user's message:\n{user_message}"
            ),
        }
    ]

    web_search_tool = {
        "type": "web_search_20260318",
        "name": "web_search",
        "max_uses": 12,
        "allowed_callers": ["direct"],
        "user_location": {
            "type": "approximate",
            "region": "California",
            "country": "US",
            "timezone": "America/Los_Angeles",
        },
    }

    try:
        response = await client.messages.create(
            model=HAPPY_MODEL,
            max_tokens=4000,
            system=HAPPY_SYSTEM_PROMPT,
            tools=[web_search_tool],
            messages=messages,
        )

        # Anthropic can occasionally pause a long web-search request.
        # This sends the response back so Claude can finish its answer.
        pause_count = 0
        maximum_pauses = 3

        while (
            response.stop_reason == "pause_turn"
            and pause_count < maximum_pauses
        ):
            messages.append(
                {
                    "role": "assistant",
                    "content": [
                        block.model_dump()
                        for block in response.content
                    ],
                }
            )

            response = await client.messages.create(
                model=HAPPY_MODEL,
                max_tokens=4000,
                system=HAPPY_SYSTEM_PROMPT,
                tools=[web_search_tool],
                messages=messages,
            )

            pause_count += 1

        answer = extract_answer_and_sources(response)

        if not answer:
            return (
                "I couldn't generate a response. "
                "Please try asking again."
            )

        return answer

    except APIError as error:
        print(f"Anthropic API error: {error}")

        return (
            "I had trouble reaching Happy's research service. "
            "Please try again."
        )

    except Exception as error:
        print(f"Unexpected Happy error: {error}")

        return (
            "Something unexpected went wrong while Happy was "
            "preparing the response. Please try again."
        )