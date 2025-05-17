from discord import Colour, Embed, Interaction

from src.comet._cli import parse_args_and_setup_logging
from src.comet.config.env import ADMIN_USER_IDS
from src.comet.db.dao.access_privilege_dao import AccessPrivilegeDAO
from src.comet.db.dao.usage_limit_dao import UsageLimitDAO
from src.comet.discord.client import BotClient
from src.comet.utils.decorators import *

client = BotClient.get_instance()
logger = parse_args_and_setup_logging()


@client.tree.command(
    name="limit",
    description="Set the daily usage limit for all regular users",
)
@is_authorized_server()  # type: ignore # noqa: F405
@is_admin_user()  # type: ignore # noqa: F405
async def limit_command(
    interaction: Interaction,
    limit: int,
) -> None:
    """Set the default daily usage limit for all regular users.

    Parameters
    ----------
    interaction : Interaction
        The interaction object from the command.
    limit : int
        The maximum number of AI calls allowed per day.
    """
    try:
        if limit < 0:
            await interaction.response.send_message(
                "**ERROR** - Please specify a positive integer for the limit.",
                ephemeral=True,
            )
            return

        dao = UsageLimitDAO()
        await dao.set_default_daily_limit(limit)

        await interaction.response.send_message(
            f"Set the daily usage limit to {limit}/day",
            ephemeral=True,
        )
        logger.info(
            "%s set default daily limit to %d",
            interaction.user,
            limit,
        )
    except Exception:
        await interaction.response.send_message(
            "**ERROR** - An error occurred while setting the limit.",
            ephemeral=True,
        )
        logger.exception("An error occurred in the limit command")


@client.tree.command(
    name="ck_limit",
    description="Check the user's current usage and limit",
)
@is_authorized_server()  # type: ignore # noqa: F405
@is_not_blocked_user()  # type: ignore # noqa: F405
async def check_limit_command(
    interaction: Interaction,
) -> None:
    """Check the user's current usage and limit.

    Parameters
    ----------
    interaction : Interaction
        The interaction object from the command.
    """
    try:
        user = interaction.user
        dao = UsageLimitDAO()
        access_dao = AccessPrivilegeDAO()

        # Check if the user is an admin or an advanced user
        is_admin = user.id in ADMIN_USER_IDS
        advanced_user_ids = await access_dao.fetch_user_ids_by_access_privilege(
            access_privilege="advanced",
        )
        is_advanced = user.id in advanced_user_ids

        user_limit = await dao.get_user_daily_limit(user.id)
        current_usage = await dao.get_user_daily_usage(user.id)

        # ------ Define discord embed style ------
        embed = Embed(
            description=f"<@{user.id}> command usage",
            color=Colour.blue(),
        )

        # Regular users have a usage limit, while advanced users and admins have unlimited usage
        if is_admin or is_advanced:
            embed.add_field(name="Usage", value=f"{current_usage} / ∞", inline=True)
            embed.add_field(name="Remaining", value="∞", inline=True)
        else:
            embed.add_field(name="Usage", value=f"{current_usage} / {user_limit}", inline=True)
            embed.add_field(
                name="Remaining",
                value=max(0, user_limit - current_usage),
                inline=True,
            )

        embed.add_field(name="Note", value="Usage is reset at 00:00 every day", inline=False)
        # ----------------------------------------

        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception:
        await interaction.response.send_message(
            "**ERROR** - An error occurred while checking the usage status.",
            ephemeral=True,
        )
        logger.exception("An error occurred in the ck_limit command")
