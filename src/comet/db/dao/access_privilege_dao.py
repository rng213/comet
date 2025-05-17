import datetime

import aiosqlite

from src.comet.config.timezone import TIMEZONE
from src.comet.db._base import SQLiteDAOBase


class AccessPrivilegeDAO(SQLiteDAOBase):
    """Data Access Object for managing user access privileges.

    Attributes
    ----------
    _table_name : str
        Name of the database table for access privileges.
    """

    _table_name: str = "access_privilege"

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
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id          INTEGER NOT NULL,
                access_privilege TEXT_NOT_NULL,
                enabled_at       DATE NOT NULL,
                disabled_at      DATE DEFAULT NULL
            );
            """
            await conn.execute(query)
            await conn.commit()
        finally:
            await conn.close()

    async def enable(self, user_id: int, access_privilege: str) -> None:
        """Enable a new access privilege for a user.

        Parameters
        ----------
        user_id : int
            The ID of the user to enable the access privilege for.
        access_privilege : str
            The access privilege to enable.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        date = datetime.datetime.now(TIMEZONE).date()
        try:
            query = """
            INSERT INTO access_privilege (user_id, access_privilege, enabled_at)
            VALUES (?, ?, ?);
            """
            await conn.execute(query, (user_id, access_privilege, date))
            await conn.commit()
        finally:
            await conn.close()

    async def fetch_user_ids_by_access_privilege(self, access_privilege: str) -> list[int]:
        """Fetch IDs of users who have a specific access privilege.

        Parameters
        ----------
        access_privilege : str
            The access privilege to filter by.

        Returns
        -------
        list[int]
            A list of user IDs that have the specified access privilege.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        try:
            query = """
            SELECT user_id FROM access_privilege WHERE access_privilege = ?
            AND disabled_at IS NULL;
            """
            cursor = await conn.execute(query, (access_privilege,))
            result = await cursor.fetchall()
            return [row[0] for row in result]
        finally:
            await conn.close()

    async def disable(self, user_id: int, access_privilege: str) -> None:
        """Disable an existing access privilege for a user.

        Parameters
        ----------
        user_id : int
            The ID of the user to disable the access privilege for.
        access_privilege : str
            The access privilege to disable.
        """
        conn = await aiosqlite.connect(super().DB_NAME)
        date = datetime.datetime.now(TIMEZONE).date()
        try:
            query = """
            UPDATE access_privilege SET disabled_at = ? WHERE user_id = ?
            AND access_privilege = ?;
            """
            await conn.execute(query, (date, user_id, access_privilege))
            await conn.commit()
        finally:
            await conn.close()
