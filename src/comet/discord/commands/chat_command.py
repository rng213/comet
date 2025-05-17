from discord import Interaction

from src.comet._cli import parse_args_and_setup_logging
from src.comet.adapters.chat import ChatMessage
from src.comet.ai.models.gpt_model import GPTModelParams
from src.comet.ai.models.storage import ModelParamsStore
from src.comet.ai.services.completion import generate_openai_response
from src.comet.config.env import (
    CHAT_MODEL,
    GPT_DEFAULT_MAX_TOKENS,
    GPT_DEFAULT_TEMPERATURE,
    GPT_DEFAULT_TOP_P,
)
from src.comet.config.yml import CHAT_SYSTEM
from src.comet.db.dao.usage_limit_dao import UsageLimitDAO
from src.comet.discord.client import BotClient
from src.comet.utils.decorators import *

client = BotClient.get_instance()
logger = parse_args_and_setup_logging()
model_params = ModelParamsStore()


@client.tree.command(name="chat", description="Single-turn chat.")
@is_not_blocked_user()  # type: ignore # noqa: F405
async def chat_command(interaction: Interaction, prompt: str) -> None:
    """Single-turn chat."""
    try:
        user = interaction.user
        logger.info("User ( %s ) is chatting with the Comet.", user)

        await interaction.response.defer()

        if CHAT_MODEL is None:
            await interaction.followup.send(
                "**ERROR** - Chat model is not set.",
                ephemeral=True,
            )
            logger.error("Chat model is not set.")
            return

        model_params = GPTModelParams(
            model=CHAT_MODEL,
            max_tokens=GPT_DEFAULT_MAX_TOKENS,
            temperature=GPT_DEFAULT_TEMPERATURE,
            top_p=GPT_DEFAULT_TOP_P,
        )

        message = ChatMessage(role="user", content=prompt)

        response = await generate_openai_response(
            system_prompt=CHAT_SYSTEM,
            prompt=[message],
            model_params=model_params,
        )

        await interaction.followup.send(f"{response.result}")

        await UsageLimitDAO().increment_usage_count(user.id)
    except Exception as err:
        msg = f"Error in chat command: {err!s}"
        logger.exception(msg)
        await interaction.followup.send(
            "**ERROR** - An error occurred while processing the chat command.",
            ephemeral=True,
        )
