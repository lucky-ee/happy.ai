# happy.ai

A private Discord research assistant built with Python, Anthropic Claude, and Discord.py.

Happy searches the web to provide a daily breakdown containing weather forecasts, local news, junior software engineering job postings, and portfolio project ideas. It also stores local notes that can be used as private context.

## Project Structure

- `happy.ai/main.py` - Runs the Discord bot and handles messages and commands
- `happy.ai/ai.py` - Connects Happy to Anthropic Claude and enables web research
- `happy.ai/memory.py` - Saves and retrieves Happy’s local notes
- `happy.ai/happy_prompt.txt` - Private system prompt ignored by Git
- `happy.ai/happy_memory.json` - Private saved memory ignored by Git
- `happy.ai/.env` - Private API keys and bot configuration ignored by Git
- `README.md` - Project documentation

## Features

- Daily weather forecasts
- Local news
- Current software engineering job postings
- Software engineering portfolio project ideas
- Web research using Anthropic Claude
- Local JSON-based memory
- Discord owner restrictions
- Source links for web-based findings

## Getting Started

### Prerequisites

- Python 3.11 or higher
- A Discord bot application
- An Anthropic API key
- A Discord server where you can install the bot

### Installation

1. Clone the repository:

```bash
git clone https://github.com/lucky-ee/happy.ai.git
cd happy.ai/happy.ai
```

2. Create a virtual environment:

```bash
python3 -m venv .venv
```

3. Activate the virtual environment:

```bash
source .venv/bin/activate
```

4. Install the dependencies:

```bash
python3 -m pip install anthropic discord.py python-dotenv
```

### Development

Start Happy:

```bash
python3 main.py
```

When the bot connects successfully, the terminal will show that Happy is online.

In Discord, request the complete daily breakdown with:

```text
!daily
```

You can also send Happy a normal message or research question.

### Discord Commands

```text
!daily      Generate the complete daily breakdown
!plan       Create a plan using saved notes
!notes      Display recent saved notes
!clear      Clear saved notes
!helphappy  Display the available commands
```

### Environment Variables

Create a `.env` file inside the `happy.ai/` directory:

```env
ANTHROPIC_API_KEY=
DISCORD_BOT_TOKEN=
HAPPY_MODEL=claude-sonnet-5

HAPPY_OWNER_ID=
HAPPY_MORNING_HOUR=8
HAPPY_MORNING_MINUTE=0
```

The `.env` file contains private credentials and must not be committed to GitHub.

### Private Prompt

Create a file named:

```text
happy_prompt.txt
```

Place Happy’s private system prompt inside this file. The file is loaded by `ai.py` and should remain excluded from GitHub.

### Git Ignore

The following files should be included in `.gitignore`:

```gitignore
# Private credentials
.env
.env.*
!.env.example

# Private Happy files
happy_memory.json
happy_prompt.txt

# Python-generated files
__pycache__/
*.pyc

# macOS-generated files
.DS_Store
```

## Privacy

Happy’s API keys, Discord token, system prompt, and saved memory are stored locally and excluded from GitHub.

Before every push, verify that the private files are not tracked:

```bash
git ls-files -- .env happy_memory.json happy_prompt.txt
```

The command should return no output.

## Team

Built by Hayley Prince, aka [lucky-ee](https://github.com/lucky-ee).

```bash
happy.ai/
├── happy.ai/
│   ├── main.py
│   ├── ai.py
│   ├── memory.py
│   ├── happy_prompt.txt
│   ├── happy_memory.json
│   ├── .env
│   └── .gitignore
└── README.md
```