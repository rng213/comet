# Prerequisites

## Python runtime environment

We recommend using uv. macOS users can install it using the following commands:

```
# with curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# with wget
wget -qO- https://astral.sh/uv/install.sh | sh

# with homebrew
brew install uv
```

Check if uv is available and install Python:

```
# Check if uv is available
uv --version

# Should display something like uv 0.6.9

# install python
uv python install 3.12.10
```

For more details, please refer to the [official documentation](https://docs.astral.sh/uv/).

## Setup Anthropic API access

Follow the steps below:

- Login to [Console Account](https://console.anthropic.com/login).
- Get the API keys.
- Keep this key safe and add it to your `.env` file under the variable `ANTHROPIC_API_KEY`.

## Setup OpenAI API access

Follow the steps below:

- Create an account on [OpenAI developer platform](https://platform.openai.com/docs/overview).
- Go to the API keys section of your account settings and generate a new API key.
- Keep this key safe and add it to your `.env` file under the variable `OPENAI_API_KEY`.

## Create and invite Discord application

1. Go to [Discord Developer Portal](https://discord.com/developers/bots), create a new discord application.

2. Go to the Bot tab and
   - Click "**Reset Token**" and keep it safe and add it to your `.env` file under the variable `DISCORD_BOT_TOKEN`.
   - Enable "**SERVER MEMBERS INTENT**" and "**MESSAGE CONTENT INTENT**".

3. Go to the OAuth2 tab and generate an invite link for your bot by picking follow scopes and permissions.

    **SCOPES**
    - application commands
    - bot

    **BOT PERMISSIONS**
    - View Channels
    - Send Messages
    - Create Public Threads
    - Send Messages in Threads
    - Manage Messages
    - Manage Threads
    - Read Message History
    - Use Slash Commands

4. Invite the bot to your guild using the generated url.
