from pathlib import Path

import yaml

with Path(__file__).parents[3].joinpath(".prompt.yml").open(encoding="utf-8") as f:
    prompt = yaml.safe_load(f)

CHAT_SYSTEM: str = prompt.get("chat_system")
FIXPY_SYSTEM: str = prompt.get("fixpy_system")
