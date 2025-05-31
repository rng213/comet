from typing import Literal

from discord import Embed, HTTPException, Interaction, app_commands

from src.comet._cli import parse_args_and_setup_logging
from src.comet.adapters.chat import ChatMessage
from src.comet.adapters.response import send_response_result
from src.comet.ai.models.claude_model import ClaudeModelParams
from src.comet.ai.models.storage import ModelParamsStore
from src.comet.ai.services.completion import generate_anthropic_response
from src.comet.config.env import (
    TALK_MAX_TOKENS,
    TALK_MODEL,
    TALK_TEMPERATURE,
    TALK_TOP_P,
)
from src.comet.config.yml import TALK_SYSTEM
from src.comet.db.dao.usage_limit_dao import UsageLimitDAO
from src.comet.discord.client import BotClient
from src.comet.utils.decorators import *

client = BotClient.get_instance()
logger = parse_args_and_setup_logging()
model_params = ModelParamsStore()

TALK_THREAD_PREFIX: Literal[">>>"] = ">>>"
system_prompt_dict: dict[int, str] = {}


@client.tree.command(name="talk", description="Create a thread and start a conversation.")
@app_commands.choices(
    model=[app_commands.Choice(name=model.name, value=model.value) for model in TALK_MODEL],
)
@is_authorized_server()  # type: ignore # noqa: F405
@is_not_blocked_user()  # type: ignore # noqa: F405
@has_daily_usage_left()  # type: ignore # noqa: F405
async def talk_command(
    interaction: Interaction,
    prompt: str,
    model: app_commands.Choice[str],
    temperature: float = TALK_TEMPERATURE,
    top_p: float = TALK_TOP_P,
) -> None:
    """Create a thread and start a conversation.

    Parameters
    ----------
    interaction : Interaction
        The interaction object from the command.
    prompt : str
        The initial message to send to the AI assistant.
    model : app_commands.Choice[str]
        The AI model to use for the conversation.
    temperature : float
        Controls randomness in response generation. Lower values make responses more deterministic.
        Must be between 0.0 and 1.0. Defaults to predefined temperature value.
    top_p : float
        Controls diversity of responses by limiting token selection to a cumulative probability.
        Must be between 0.0 and 1.0. Defaults to predefined top_p value.
    """
    try:
        user = interaction.user
        logger.info("User ( %s ) is executing the talk command.", user)

        await interaction.response.defer()

        embed = Embed(
            description=f"<@{user.id}> **initiated the chat!**",
            color=0xF4B3C2,
        )
        embed.add_field(name="model", value=model.name, inline=True)
        embed.add_field(name="temperature", value=temperature, inline=True)
        embed.add_field(name="top_p", value=top_p, inline=True)
        embed.add_field(name="message", value=prompt)

        await interaction.followup.send(embed=embed)
        original_response = await interaction.original_response()

        # Create the thread
        thread = await original_response.create_thread(
            name=f"{TALK_THREAD_PREFIX} {prompt[:30]}",
            auto_archive_duration=60,
            slowmode_delay=1,
        )
        system_prompt_dict[thread.id] = TALK_SYSTEM
        model_params.set_model_params(
            thread.id,
            ClaudeModelParams(
                model=model.value,
                max_tokens=TALK_MAX_TOKENS,
                temperature=temperature,
                top_p=top_p,
            ),
        )

        async with thread.typing():
            messages = [ChatMessage(role=user.name, content=prompt)]
            response = await generate_anthropic_response(
                system_prompt=TALK_SYSTEM,
                prompt=messages,
                model_params=model_params.get_model_params(thread.id),
            )

        # Increment the usage count for the user
        await UsageLimitDAO().increment_usage_count(user.id)

        await send_response_result(thread=thread, result=response)
    except HTTPException as err:
        msg = f"HTTPException occurred in the talk command: {err!s}"
        logger.exception(msg)
        await interaction.followup.send(
            "**ERROR** - HTTPException occurred in the talk command.",
            ephemeral=True,
        )
    except Exception as err:
        msg = f"An error occurred in the talk command: {err!s}"
        logger.exception(msg)
        await interaction.followup.send(
            "**ERROR** - An error occurred in the talk command.",
            ephemeral=True,
        )
