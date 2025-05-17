import asyncio
import os
import signal
from collections.abc import Generator
from contextlib import contextmanager

from dotenv import load_dotenv

from src.comet._cli import parse_args_and_setup_logging
from src.comet.db.dao.access_privilege_dao import AccessPrivilegeDAO
from src.comet.db.dao.usage_limit_dao import UsageLimitDAO
from src.comet.discord.client import BotClient
from src.comet.discord.commands import *
from src.comet.discord.event import *
from src.comet.utils.scheduler import TaskScheduler


@contextmanager
def ignore_signals(signals: list[signal.Signals]) -> Generator[None, None, None]:
    """Temporarily ignore specified signals.

    Parameters
    ----------
    signals : list[signal.Signals]
        A list of signals to ignore.

    Examples
    --------
    >>> with ignore_signals([signal.SIGTERM, signal.SIGINT]):
    ...     # processes whose signals are ignored
    ...     pass
    """
    original_handlers = {sig: signal.getsignal(sig) for sig in signals}
    try:
        for sig in signals:
            signal.signal(sig, signal.SIG_IGN)
        yield
    finally:
        for sig, handler in original_handlers.items():
            signal.signal(sig, handler)


async def main() -> None:
    """Entry point for the 'comet'."""
    logger = parse_args_and_setup_logging()

    # Initialize database tables
    await AccessPrivilegeDAO().create_table()
    await UsageLimitDAO().create_table()
    await UsageLimitDAO().create_commands_usage_table()

    # Start the usage reset scheduler and store the task reference
    reset_scheduler_task = asyncio.create_task(TaskScheduler.start_reset_usage_scheduler())
    logger.info("Started usage reset scheduler")

    load_dotenv()
    # This environment variable is specific to this function
    DISCORD_BOT_TOKEN: str = os.environ["DISCORD_BOT_TOKEN"]  # noqa: N806

    client = BotClient.get_instance()

    try:
        await client.start(DISCORD_BOT_TOKEN)
    except Exception:
        logger.exception("An unexpected error occurred")
    finally:
        with ignore_signals([signal.SIGTERM, signal.SIGINT]):
            # Cancel the scheduler task before cleanup
            if not reset_scheduler_task.done():
                reset_scheduler_task.cancel()
            await client.cleanup_hook()
            logger.info("Cleanup process finished")


if __name__ == "__main__":
    asyncio.run(main())
