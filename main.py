import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

import memory
import ai


ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)

# These fallbacks let your existing .env names continue working.
DISCORD_BOT_TOKEN = (
    os.getenv("HAPPY_DISCORD_BOT_TOKEN")
    or os.getenv("DISCORD_BOT_TOKEN")
)

HAPPY_OWNER_ID = (
    os.getenv("HAPPY_OWNER_ID")
    or os.getenv("ALBIE_OWNER_ID")
)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


def is_owner(user_id):
    if not HAPPY_OWNER_ID:
        return True

    return str(user_id) == str(HAPPY_OWNER_ID)


async def send_long_message(channel, text):
    if len(text) <= 1900:
        await channel.send(text)
        return

    for i in range(0, len(text), 1900):
        await channel.send(text[i:i + 1900])


@bot.event
async def on_ready():
    print(f"Happy is online as {bot.user}")


@bot.event
async def on_message(message):
    # Debug information.
    print("\n--- NEW MESSAGE DETECTED ---")
    print(f"Author: {message.author} (ID: {message.author.id})")
    print(f"Content: '{message.content}'")

    # Ignore messages sent by Happy itself.
    if message.author == bot.user:
        return

    # Ignore messages from anyone other than the owner.
    if not is_owner(message.author.id):
        print(f"❌ Blocked: {message.author} is not the owner.")
        return

    print("✅ Passed: Processing message for Happy...")

    content = message.content.strip()

    if not content:
        return

    # Allow Discord commands to run.
    await bot.process_commands(message)

    # Do not save commands as notes.
    if content.startswith("!"):
        return

    if content.lower() in [
        "plan",
        "today",
        "what should i do today"
    ]:
        async with message.channel.typing():
            try:
                notes = memory.get_recent_notes()

                reply = await ai.ask_happy(
                    "Make my plan for today based on my saved notes.",
                    notes
                )

                await send_long_message(message.channel, reply)

            except Exception as error:
                print(f"Plan error: {error}")

                await message.channel.send(
                    f"⚠️ Error: {error}"
                )

        return

    # Save the message, but answer it like a normal AI request.
    # Retrieve earlier notes first so the current message is not duplicated
    # in both the request and memory context.
    notes = memory.get_recent_notes()
    memory.add_note(content)

    async with message.channel.typing():
        try:
            reply = await ai.ask_happy(content, notes)

            await send_long_message(message.channel, reply)

        except Exception as error:
            print(f"Happy response error: {error}")

            await message.channel.send(
                f"✅ Message saved, but error generating reply: {error}"
            )


@bot.command(name="plan")
async def plan_command(ctx):
    if not is_owner(ctx.author.id):
        return

    async with ctx.typing():
        try:
            notes = memory.get_recent_notes()

            reply = await ai.ask_happy(
                "Make my plan for today based on my saved notes.",
                notes
            )

            await send_long_message(ctx.channel, reply)

        except Exception as error:
            print(f"Plan command error: {error}")

            await ctx.send(
                f"⚠️ An error occurred: `{error}`"
            )


@bot.command(name="daily")
async def daily_command(ctx):
    if not is_owner(ctx.author.id):
        return

    async with ctx.typing():
        try:
            notes = memory.get_recent_notes()

            reply = await ai.ask_happy(
                """
Give me my complete daily breakdown for today.

Include:
- today's weather for San Francisco, Fairfield, and Davis/UC Davis
- important recent news for those areas and California
- currently active junior or entry-level software engineering jobs
  in San Francisco and the Bay Area
- one useful junior software engineering portfolio project idea
- any relevant tasks or priorities from my saved notes

Use current web information and exact dates.
""",
                notes
            )

            await send_long_message(ctx.channel, reply)

        except Exception as error:
            print(f"Daily command error: {error}")

            await ctx.send(
                f"⚠️ An error occurred: `{error}`"
            )


@bot.command(name="notes")
async def notes_command(ctx):
    if not is_owner(ctx.author.id):
        return

    notes = memory.get_recent_notes()

    if not notes:
        await ctx.send(
            "You do not have any saved notes yet."
        )
        return

    text = "**Recent saved notes:**\n\n"

    for note in notes:
        text += (
            f"- {note['date']} {note['time']}: "
            f"{note['text']}\n"
        )

    await send_long_message(ctx.channel, text)


@bot.command(name="clear")
async def clear_command(ctx):
    if not is_owner(ctx.author.id):
        return

    memory.clear_memory()
    await ctx.send("Cleared your saved notes.")


@bot.command(name="helphappy")
async def helphappy_command(ctx):
    help_text = """
**Happy commands**
`!daily` - Get your full daily breakdown
`!plan` - Make your plan
`!notes` - Show saved notes
`!clear` - Clear saved notes
`!helphappy` - Show this help message
"""

    await ctx.send(help_text)


if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        raise ValueError(
            "Missing HAPPY_DISCORD_BOT_TOKEN or "
            "DISCORD_BOT_TOKEN in .env"
        )

    bot.run(DISCORD_BOT_TOKEN)