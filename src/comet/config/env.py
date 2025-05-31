from __future__ import annotations

import os

from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

# Base
BASE_TOP_P: float = float(os.environ["BASE_TOP_P"])

# Claude
CLAUDE_DEFAULT_CONTEXT_WINDOW: int = int(os.environ["CLAUDE_DEFAULT_CONTEXT_WINDOW"])
CLAUDE_DEFAULT_MAX_TOKENS: int = int(os.environ["CLAUDE_DEFAULT_MAX_TOKENS"])
CLAUDE_DEFAULT_TEMPERATURE: float = float(os.environ["CLAUDE_DEFAULT_TEMPERATURE"])
CLAUDE_DEFAULT_TOP_P: float = float(os.environ["CLAUDE_DEFAULT_TOP_P"])

# Database
SQLITE_DB_NAME: str = os.environ["SQLITE_DB_NAME"]

# Discord
ADMIN_USER_IDS: list[int] = [
    int(id_str) for id_str in os.environ["ADMIN_USER_IDS"].split(",") if id_str.strip()
]
AUTHORIZED_SERVER_IDS: list[int] = [
    int(id_str) for id_str in os.environ["AUTHORIZED_SERVER_IDS"].split(",") if id_str.strip()
]
BOT_NAME: str = os.environ["BOT_NAME"]
MAX_CHARS_PER_MESSAGE: int = int(os.environ["MAX_CHARS_PER_MESSAGE"])

# GPT
GPT_DEFAULT_CONTEXT_WINDOW: int = int(os.environ["GPT_DEFAULT_CONTEXT_WINDOW"])
GPT_DEFAULT_MAX_TOKENS: int = int(os.environ["GPT_DEFAULT_MAX_TOKENS"])
GPT_DEFAULT_TEMPERATURE: float = float(os.environ["GPT_DEFAULT_TEMPERATURE"])
GPT_DEFAULT_TOP_P: float = float(os.environ["GPT_DEFAULT_TOP_P"])

# Each Command
CHAT_MODEL: str = os.environ["CHAT_MODEL"]

# '/fixpy' command
FIXPY_MODEL: str = os.environ["FIXPY_MODEL"]
FIXPY_TEMPERATURE: float = float(os.environ["FIXPY_TEMPERATURE"])
FIXPY_TOP_P: float = float(os.environ["FIXPY_TOP_P"])

# '/talk' command
TALK_MAX_TOKENS: int = int(os.environ["TALK_MAX_TOKENS"])
TALK_TEMPERATURE: float = float(os.environ["TALK_TEMPERATURE"])
TALK_TOP_P: float = float(os.environ["TALK_TOP_P"])


def _get_model_choices(env_var: str) -> list[app_commands.Choice[str]]:
    models_str = os.environ[env_var]
    choices: list[app_commands.Choice[str]] = []
    if models_str:
        for entry in models_str.split(","):
            entry_stripped = entry.strip()
            if not entry_stripped:
                msg = "Empty entry found in environment variable."
                raise ValueError(msg)
            try:
                name, value_str = entry_stripped.split(":")
                value: str = value_str
            except ValueError as err:
                msg = "Invalid format in environment variable, expected 'name:value'."
                raise ValueError(msg) from err
            choices.append(app_commands.Choice(name=name, value=value))
    return choices


TALK_MODEL = _get_model_choices("TALK_MODEL")
