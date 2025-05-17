import asyncio
import datetime
from collections.abc import Callable, Coroutine
from typing import TypeVar

from src.comet._cli import parse_args_and_setup_logging
from src.comet.config.timezone import TIMEZONE
from src.comet.db.dao.usage_limit_dao import UsageLimitDAO

_T = TypeVar("_T")
logger = parse_args_and_setup_logging()


class TaskScheduler:
    """Scheduler for running tasks at specific times.

    This class provides functionality to schedule tasks to run at
    specific times, such as daily at midnight.
    """

    @staticmethod
    async def _wait_until(dt: datetime.datetime) -> None:
        """Wait until a specific datetime.

        Parameters
        ----------
        dt : datetime.datetime
            Target datetime to wait for.
        """
        now = datetime.datetime.now(TIMEZONE)
        if dt < now:
            # If the target time is in the past, add one day
            dt = dt + datetime.timedelta(days=1)

        # Calculate seconds until the target time
        wait_seconds = (dt - now).total_seconds()
        logger.info("Waiting for %s seconds until %s", wait_seconds, dt)
        await asyncio.sleep(wait_seconds)

    @staticmethod
    async def _schedule_daily(
        time: datetime.time,
        task: Callable[[], Coroutine[None, None, _T]],
    ) -> None:
        """Schedule a task to run daily at a specific time.

        Parameters
        ----------
        time : datetime.time
            Time of day to run the task.
        task : Callable[[], Coroutine[None, None, T]]
            Coroutine function to execute.
        """
        while True:
            # Next run datetime
            now = datetime.datetime.now(TIMEZONE)
            next_run = datetime.datetime.combine(now.date(), time, TIMEZONE)

            # If it's already past the time today, schedule for tomorrow
            if now.time() > time:
                next_run = next_run + datetime.timedelta(days=1)

            # Wait until the scheduled time
            await TaskScheduler._wait_until(next_run)

            # Execute the task
            try:
                logger.info("Running scheduled task at %s", next_run)
                await task()
                logger.info("Scheduled task completed successfully")
            except Exception:
                logger.exception("Error in scheduled task")

            # Wait a bit to avoid running the task twice if execution is very fast
            await asyncio.sleep(1)

    @staticmethod
    async def start_reset_usage_scheduler() -> None:
        """Start scheduler to reset usage counts at midnight."""
        # Reset time - midnight (00:00:00)
        reset_time = datetime.time(0, 0, 0, tzinfo=TIMEZONE)

        async def reset_all_usage() -> None:
            logger.info("Resetting all user commands usage counts")
            await UsageLimitDAO().DELETE_ALL_USAGE_COUNTS()
            logger.info("Successfully reset all user commands usage counts")

        # Start the scheduler
        await TaskScheduler._schedule_daily(reset_time, reset_all_usage)
