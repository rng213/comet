import datetime
from typing import cast

import aiosqlite

from src.comet.config.timezone import TIMEZONE
from src.comet.db._base import SQLiteDAOBase


class UsageLimitDAO(SQLiteDAOBase):
    """Data Access Object for managing command usage limits.

    Attributes
    ----------
    _table_name : str
        Name of the database table for command usage limits.
    """

    _table_name: str = "usage_limit"

    async def create_table(self) -> None:
        """Create table if it doesn't exist.

        Raises
        ------
        ValueError
            If the table name contains invalid characters.
        """
        if not self.validate_table_name(self._table_name):
            msg = "Invalid tablename: Only alphanumeric characters and underscores are allowed."
            raise ValueError(msg)

        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = f"""
            CREATE TABLE IF NOT EXISTS {self._table_name} (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER NOT NULL UNIQUE,
                daily_limit  INTEGER NOT NULL DEFAULT 10,
                last_updated TIMESTAMP NOT NULL
            );
            """
            await conn.execute(query)
            await conn.commit()
        finally:
            await conn.close()

    async def create_commands_usage_table(self) -> None:
        """Create table for tracking commands usage if it doesn't exist.

        Raises
        ------
        ValueError
            If the table name contains invalid characters.
        """
        _table_name = "commands_usage"
        if not self.validate_table_name(self._table_name):
            msg = "Invalid tablename: Only alphanumeric characters and underscores are allowed."
            raise ValueError(msg)

        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = f"""
            CREATE TABLE IF NOT EXISTS {_table_name} (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                usage_date  DATE NOT NULL,
                usage_count INTEGER NOT NULL DEFAULT 0,
                UNIQUE(user_id, usage_date)
            );
            """
            await conn.execute(query)
            await conn.commit()
        finally:
            await conn.close()

    async def set_default_daily_limit(self, daily_limit: int) -> None:
        """Set or update the default daily usage limit for all users.

        Parameters
        ----------
        daily_limit : int
            The maximum number of commands calls allowed per day.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        now = datetime.datetime.now(TIMEZONE)
        try:
            # Use a special user_id (0) to represent the default limit
            query = """
            INSERT INTO usage_limit (user_id, daily_limit, last_updated)
            VALUES (0, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                daily_limit = ?,
                last_updated = ?
            """
            await conn.execute(query, (daily_limit, now, daily_limit, now))
            await conn.commit()
        finally:
            await conn.close()

    async def get_default_daily_limit(self) -> int:
        """Get the default daily usage limit for regular users.

        Returns
        -------
        int
            Default maximum number of API calls allowed per day.
            Returns 10 if no default limit is set.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = """
            SELECT daily_limit FROM usage_limit WHERE user_id = 0
            """
            cursor = await conn.execute(query)
            row = await cursor.fetchone()
            return cast("int", row[0] if row else 10)  # Default limit is 10
        finally:
            await conn.close()

    async def increment_usage_count(self, user_id: int) -> None:
        """Increment the usage count for a user on the current day.

        Parameters
        ----------
        user_id : int
            ID of the user to increment usage for.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        today = datetime.datetime.now(TIMEZONE).date()
        try:
            query = """
            INSERT INTO commands_usage (user_id, usage_date, usage_count)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, usage_date) DO UPDATE SET
                usage_count = usage_count + 1
            """
            await conn.execute(query, (user_id, today))
            await conn.commit()
        finally:
            await conn.close()

    async def get_user_daily_limit(self, user_id: int) -> int:
        """Get daily usage limit for a user.

        Parameters
        ----------
        user_id : int
            ID of the user to get the limit for.

        Returns
        -------
        int
            Maximum number of API calls allowed per day.
            Returns 10 as default if no limit is set.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = """
            SELECT daily_limit FROM usage_limit WHERE user_id = ?
            """
            cursor = await conn.execute(query, (user_id,))
            row = await cursor.fetchone()

            if row:
                return cast("int", row[0])

            # If no user-specific limit is set, get the default limit
            return await self.get_default_daily_limit()
        finally:
            await conn.close()

    async def get_user_daily_usage(self, user_id: int) -> int:
        """Get the current day's usage count for a user.

        Parameters
        ----------
        user_id : int
            ID of the user to get usage for.

        Returns
        -------
        int
            Number of commands calls used today. Returns 0 if no record found.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        today = datetime.datetime.now(TIMEZONE).date()
        try:
            query = """
            SELECT usage_count FROM commands_usage
            WHERE user_id = ? AND usage_date = ?
            """
            cursor = await conn.execute(query, (user_id, today))
            row = await cursor.fetchone()
            return row[0] if row else 0
        finally:
            await conn.close()

    # This function is dangerous (deleting data)
    async def DELETE_ALL_USAGE_COUNTS(self) -> None:  # noqa: N802
        """Reset all usage counts by removing records from current day."""
        conn = await aiosqlite.connect(super().DB_NAME)
        yesterday = (datetime.datetime.now(TIMEZONE) - datetime.timedelta(days=1)).date()
        try:
            # Delete data older than yesterday
            query = """
            DELETE FROM commands_usage
            WHERE usage_date < ?
            """
            await conn.execute(query, (yesterday,))
            await conn.commit()
        finally:
            await conn.close()
