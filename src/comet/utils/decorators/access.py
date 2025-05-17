from collections.abc import Callable
from typing import TypeVar

from discord import Interaction, app_commands

from src.comet.config.env import ADMIN_USER_IDS, AUTHORIZED_SERVER_IDS
from src.comet.db.dao.access_privilege_dao import AccessPrivilegeDAO
from src.comet.db.dao.usage_limit_dao import UsageLimitDAO

_T = TypeVar("_T")
access_dao = AccessPrivilegeDAO()


def is_authorized_server() -> Callable[[_T], _T]:
    """Check if the server has been authorized by bot owner.

    Returns
    -------
    Callable[[_T], _T]
        A decorator checks whether the server is listed in the
        environment variable `AUTHORIZED_SERVER_IDS`.
    """

    def predicate(interaction: Interaction) -> bool:
        return interaction.guild_id in AUTHORIZED_SERVER_IDS

    return app_commands.check(predicate)


def is_admin_user() -> Callable[[_T], _T]:
    """Check if the user has administrative access privilege.

    Returns
    -------
    Callable[[_T], _T]
        A decorator that checks whether the user executing command is listed
        in the environment variable `ADMIN_USER_IDS`.
    """

    def predicate(interaction: Interaction) -> bool:
        return interaction.user.id in ADMIN_USER_IDS

    return app_commands.check(predicate)


def is_advanced_user() -> Callable[[_T], _T]:
    """Check if the user has advanced access privilege.

    Returns
    -------
    Callable[[_T], _T]
        A decorator that checks whether the user executing command is listed
        in the table `access_privilege` with `advanced` access privilege.
    """

    async def predicate(interaction: Interaction) -> bool:
        advanced_user_ids = await access_dao.fetch_user_ids_by_access_privilege(
            access_privilege="advanced",
        )
        return interaction.user.id in advanced_user_ids

    return app_commands.check(predicate)


def is_not_blocked_user() -> Callable[[_T], _T]:
    """Check if the user had not been blocked.

    Returns
    -------
    Callable[[_T], _T]
        A decorator that checks whether the user executing command is not listed
        in the table `blocked_user` with `blocked` access privilege.
    """

    async def predicate(interaction: Interaction) -> bool:
        blocked_user_ids = await access_dao.fetch_user_ids_by_access_privilege(
            access_privilege="blocked",
        )
        return interaction.user.id not in blocked_user_ids

    return app_commands.check(predicate)


def has_daily_usage_left() -> Callable[[_T], _T]:
    """Check if the user has not reached their daily usage limit.

    Returns
    -------
    Callable[[_T], _T]
        A decorator that checks whether the user has not reached
        their daily limit of usage.
    """

    async def predicate(interaction: Interaction) -> bool:
        # Admin users bypass the daily usage limit check
        if interaction.user.id in ADMIN_USER_IDS:
            return True

        # Advanced users bypass the daily usage limit check
        advanced_user_ids = await access_dao.fetch_user_ids_by_access_privilege(
            access_privilege="advanced",
        )
        if interaction.user.id in advanced_user_ids:
            return True

        usage_dao = UsageLimitDAO()

        current_usage = await usage_dao.get_user_daily_usage(interaction.user.id)
        user_limit = await usage_dao.get_user_daily_limit(interaction.user.id)

        result: bool = current_usage < user_limit

        return result

    return app_commands.check(predicate)
