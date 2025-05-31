# Comet

![Python](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white&style=flat&labelColor=24292e)
![License](https://img.shields.io/badge/License-BSD--3--Clause-orange.svg?style=flat&labelColor=24292e)

**Comet** is an AI-powered Discord Bot.

## Getting Started

### Prerequisites

The following preparations are required:
- Python runtime environment
- Anthropic API Key
- OpenAI API Key
- Discord Bot configuration

For detailed information, please refer to [PREREQUISITES.md](https://github.com/rng213/comet/blob/main/docs/PREREQUISITES.md).


### Set up

**1. Clone repository and install dependencies**

```
# ----- clone repo -----
git clone https://github.com/rng213/comet.git
cd comet/

# ----- install dependencies -----
# with uv
uv sync

# without uv
pip install -r requirements.txt
```

**2. Prepare env file**

This application requires a `.env` file for configuration. Follow these steps:

1. Copy the `.env.example` file and rename it to `.env`
2. Fill in all the required values in the `.env` file

**3. Write system prompts**

> [!IMPORTANT]
> When operating on a public server, it is strongly recommended to use robust system prompts with appropriate security measures in place.

Make a copy of `.prompt.yml.sample` and rename it to `.prompt.yml`. Set system prompts for each feature.

Example:

```yaml
# For `/chat` command
chat_system: |
  You are a helpful assistant that strictly follows the [System Instructions].

  # [System Instructions]

  Detail instructions...
```

### Run the Bot

Finally, make sure all values in the `.env` file and `.prompt.yml` file are filled in correctly, and then execute the following:

```
python -m src.comet --log <log_level>
```

**Note**: The `--log <log_level>` parameter is optional and allows you to set the log level. Available values are DEBUG, INFO, WARNING, ERROR, CRITICAL. If not specified, INFO will be used as default.
