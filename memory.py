import json
from datetime import datetime
from pathlib import Path


# Save happy_memory.json in the same folder as memory.py.
MEMORY_FILE = Path(__file__).resolve().parent / "happy_memory.json"


def load_memory():
    """
    Load Happy's saved memory.

    If the memory file does not exist or cannot be read,
    return an empty notes list.
    """

    if not MEMORY_FILE.exists():
        return {"notes": []}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            memory = json.load(file)

        # Make sure the expected notes list exists.
        if "notes" not in memory:
            memory["notes"] = []

        return memory

    except (json.JSONDecodeError, OSError):
        return {"notes": []}


def save_memory(memory):
    """
    Save Happy's memory to happy_memory.json.
    """

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            memory,
            file,
            indent=2,
            ensure_ascii=False
        )


def add_note(text):
    """
    Add a new note to Happy's memory.
    """

    memory = load_memory()
    now = datetime.now()

    note = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%I:%M %p"),
        "text": text,
    }

    memory["notes"].append(note)
    save_memory(memory)


def get_recent_notes(limit=20):
    """
    Return Happy's most recent saved notes.
    """

    memory = load_memory()
    notes = memory.get("notes", [])

    return notes[-limit:]


def clear_memory():
    """
    Clear all of Happy's saved notes.
    """

    save_memory({"notes": []})