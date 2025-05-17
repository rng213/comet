from discord import Colour, Embed, Interaction, Thread, app_commands
from discord import Message as DiscordMessage

from src.comet._cli import parse_args_and_setup_logging
from src.comet.adapters.chat import ChatMessage
from src.comet.adapters.response import send_response_result
from src.comet.ai.models.storage import ModelParamsStore
from src.comet.ai.services.completion import generate_anthropic_response
from src.comet.config.env import ADMIN_USER_IDS, CLAUDE_DEFAULT_CONTEXT_WINDOW
from src.comet.db.dao.access_privilege_dao import AccessPrivilegeDAO
from src.comet.db.dao.usage_limit_dao import UsageLimitDAO
from src.comet.discord.client import BotClient
from src.comet.discord.commands import *

access_dao = AccessPrivilegeDAO()
client = BotClient.get_instance()
logger = parse_args_and_setup_logging()
model_params = ModelParamsStore()


async def _check_user_daily_limit(user_id: int) -> bool:
    """Check if a user has reached their daily API usage limit.

    Parameters
    ----------
    user_id : int
        The Discord user ID to check

    Returns
    -------
    bool
        True if the user has not reached their limit, False if they have
    """
    # Admin users bypass usage limits
    if user_id in ADMIN_USER_IDS:
        return True

    # Advanced users bypass usage limits
    advanced_user_ids = await access_dao.fetch_user_ids_by_access_privilege(
        access_privilege="advanced",
    )
    if user_id in advanced_user_ids:
        return True

    # Check usage limits for regular users
    usage_dao = UsageLimitDAO()
    current_usage = await usage_dao.get_user_daily_usage(user_id)
    user_limit = await usage_dao.get_user_daily_limit(user_id)

    result: bool = current_usage < user_limit

    return result


async def _close_thread(thread: Thread) -> None:
    await thread.send(
        embed=Embed(
            description="context reached limit, closing thread",
            color=Colour.light_grey(),
        ),
    )
    await thread.edit(archived=False, locked=True)


async def _get_conversation_history(thread: Thread, limit: int) -> list:
    # Fetch conversation history from Discord thread and convert it to a list of ChatMessage
    convo_history = [
        await ChatMessage.from_discord_message(msg) async for msg in thread.history(limit=limit)
    ]
    # Filter out any None messages
    convo_history = [msg for msg in convo_history if msg is not None]
    # Reverse the conversation history to have oldest messages first
    convo_history.reverse()

    return convo_history


async def _handle_claude_thread(discord_msg: DiscordMessage) -> None:
    if not isinstance(discord_msg.channel, Thread):
        return

    thread: Thread = discord_msg.channel

    if thread.message_count > CLAUDE_DEFAULT_CONTEXT_WINDOW:
        await _close_thread(thread)
        return

    if not await _check_user_daily_limit(discord_msg.author.id):
        msg = "**You have reached the usage limit for today. It will be reset at 00:00.**"
        await thread.send(
            embed=Embed(
                description=msg,
                color=Colour.red(),
            ),
        )
        return

    try:
        convo_history = await _get_conversation_history(thread, CLAUDE_DEFAULT_CONTEXT_WINDOW)

        async with thread.typing():
            response = await generate_anthropic_response(
                # コマンドファイル内で定義し、ワイルドカードインポートする
                # 実装後コメントは削除する
                system_prompt=system_prompt_dict.get(  # type: ignore # noqa: F405
                    thread.id,
                ),
                prompt=convo_history,
                model_params=model_params.get_model_params(
                    thread.id,
                ),
            )

        # Increment usage count
        await UsageLimitDAO().increment_usage_count(discord_msg.author.id)

        await send_response_result(thread=discord_msg.channel, result=response)
    except Exception as err:
        error_msg = f"Error occurred while processing message: {err!s}"
        logger.exception(error_msg)

        await thread.send(
            embed=Embed(
                description="**ERROR** - An error occurred while handling thread.",
                color=Colour.red(),
            ),
        )


async def _is_valid_message(discord_msg: DiscordMessage) -> bool:
    # Get the user id that has access type "blocked"
    blocked_user_ids = await access_dao.fetch_user_ids_by_access_privilege(
        access_privilege="blocked",
    )

    return not (
        # Ignore messages from the bot
        # Blocked user can't use the bot
        # Ignore messages not in a thread
        # Ignore threads not created by the bot
        # Ignore threads that are archived, locked or title is not what we expected
        # Ignore threads that have too many messages
        discord_msg.author == client.user
        or discord_msg.author.id in blocked_user_ids
        or not isinstance(discord_msg.channel, Thread)
        or client.user is None
        or discord_msg.channel.owner_id != client.user.id
        or discord_msg.channel.archived
        or discord_msg.channel.locked
    )


@client.event
async def on_message(user_msg: DiscordMessage) -> None:
    """Event handler for Discord message events.

    Parameters
    ----------
    user_msg : DiscordMessage
        A message received from discord.
    """
    try:
        if not await _is_valid_message(user_msg):
            return

        # Chat with claude
        if isinstance(user_msg.channel, Thread) and user_msg.channel.name.startswith(
            # mypy(name-defined): Defined in a wildcard import
            CLAUDE_THREAD_PREFIX,  # type: ignore # noqa: F405
        ):
            await _handle_claude_thread(user_msg)
    except Exception:
        logger.exception("An error occurred in the on_message event")
        await user_msg.channel.send(
            embed=Embed(
                description="**ERROR** - An error occurred while processing (on_message).",
                color=Colour.red(),
            ),
        )


@client.tree.error
async def on_app_command_error(
    interaction: Interaction,
    error: app_commands.AppCommandError,
) -> None:
    """Event handler for app command errors.

    Parameters
    ----------
    interaction : Interaction
        The interaction that caused the error.
    error : app_commands.AppCommandError
        The error that occurred.
    """
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message(
            "**CheckFailure** - You do not have permission to use this command.",
            ephemeral=True,
        )
