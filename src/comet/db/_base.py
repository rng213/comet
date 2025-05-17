import re

from src.comet.config.env import SQLITE_DB_NAME


class SQLiteDAOBase:
    DB_NAME: str = SQLITE_DB_NAME

    @staticmethod
    def validate_table_name(table_name: str) -> bool:
        """Only letters, numbers, and underscores are allowed."""
        pattern = r"^[A-Za-z0-9_]+$"
        return bool(re.match(pattern, table_name))
