from discord import Interaction, SelectOption, User
from discord.ui import Select, View

from src.comet._cli import parse_args_and_setup_logging
from src.comet.db.dao.access_privilege_dao import AccessPrivilegeDAO
from src.comet.discord.client import BotClient
from src.comet.utils.decorators import *

access_dao = AccessPrivilegeDAO()
client = BotClient.get_instance()
logger = parse_args_and_setup_logging()


class AccessGrantSelector(Select):
    """Discord UI selector for granting access privileges to users.

    This class creates a dropdown menu that allows administrators to
    select access privileges ('advanced' or 'blocked') to grant to a user.

    Parameters
    ----------
    user_id : int
        The Discord user ID to grant access to.
    options : list[SelectOption]
        List of SelectOption objects representing available access privileges.
    """

    def __init__(self, user_id: int, options: list[SelectOption]) -> None:
        self.user_id = user_id
        super().__init__(
            placeholder="Select a access privilege ...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: Interaction) -> None:
        """Handle the user's selection of access privilege to grant.

        Parameters
        ----------
        interaction : Interaction
            The Discord interaction context.

        Notes
        -----
        This callback inserts the selected access privilege for the user into the database
        and sends a confirmation message.
        """
        chosen = self.values[0]  # "advanced" or "blocked"
        if chosen == "advanced":
            await access_dao.enable(user_id=self.user_id, access_privilege="advanced")
        elif chosen == "blocked":
            await access_dao.enable(user_id=self.user_id, access_privilege="blocked")

        await interaction.response.send_message(
            f"Access privilege `{chosen}` has been added to the user (ID: `{self.user_id}`)",
            ephemeral=True,
        )
        logger.info(
            "Access privilege <%s> has been added to the user (ID: %s)",
            chosen,
            self.user_id,
        )


class AccessDisableSelector(Select):
    """Discord UI selector for disabling access privileges for users.

    This class creates a dropdown menu that allows administrators to
    select access privileges ('advanced' or 'blocked') to disable for a user.

    Parameters
    ----------
    user_id : int
        The Discord user ID to disable access for.
    options : list[SelectOption]
        List of SelectOption objects representing available access types.
    """

    def __init__(self, user_id: int, options: list[SelectOption]) -> None:
        self.user_id = user_id
        super().__init__(
            placeholder="Select an access privilege...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: Interaction) -> None:
        """Handle the user's selection of access privilege to disable.

        Parameters
        ----------
        interaction : Interaction
            The Discord interaction context.

        Notes
        -----
        This callback disables the selected access privilege for the user in the database
        and sends a confirmation message.
        """
        chosen = self.values[0]  # "advanced" or "blocked"
        if chosen == "advanced":
            await access_dao.disable(user_id=self.user_id, access_privilege="advanced")
        elif chosen == "blocked":
            await access_dao.disable(user_id=self.user_id, access_privilege="blocked")

        await interaction.response.send_message(
            f"Access privilege `{chosen}` has been disabled for the user (ID: `{self.user_id}`)",
            ephemeral=True,
        )
        logger.info(
            "Access privilege <%s> has been disabled for the user (ID: %s)",
            chosen,
            self.user_id,
        )


@client.tree.command(name="grant_access", description="Grant an access privilege to the user")
@is_authorized_server()  # type: ignore # noqa: F405
@is_admin_user()  # type: ignore # noqa: F405
async def grant_access_command(interaction: Interaction, user: User) -> None:
    """Grant access type to a Discord user.

    Parameters
    ----------
    interaction : Interaction
        The Discord interaction context.
    user : User
        The target Discord user to grant access to.

    Notes
    -----
    This function grants 'advanced' or 'blocked' access privilege to the specified user.
    """
    target_user_id = user.id
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used in a guild",
            ephemeral=True,
        )
        return

    target_user = interaction.guild.get_member(target_user_id)
    if target_user is None:
        await interaction.response.send_message(
            "The user does not exist in the guild",
            ephemeral=True,
        )
        return

    options = [
        SelectOption(label="advanced", value="advanced"),
        SelectOption(label="blocked", value="blocked"),
    ]

    select = AccessGrantSelector(user_id=target_user_id, options=options)
    view = View()
    view.add_item(select)

    await interaction.response.send_message(
        "Select an access privilege to grant to the user",
        view=view,
        ephemeral=True,
    )


@client.tree.command(name="ck_access", description="Check the access privilege of the user")
@is_authorized_server()  # type: ignore # noqa: F405
@is_admin_user()  # type: ignore # noqa: F405
async def check_access_command(interaction: Interaction, user: User) -> None:
    """Check the access type of a Discord user.

    Parameters
    ----------
    interaction : Interaction
        The Discord interaction context.
    user : User
        The target Discord user to check access for.

    Notes
    -----
    This function displays whether the user has 'advanced' or 'blocked' access privilege.
    """
    target_user_id = user.id
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used in a guild",
            ephemeral=True,
        )
        return

    target_user = interaction.guild.get_member(target_user_id)
    if target_user is None:
        await interaction.response.send_message(
            "The user does not exist in the guild",
            ephemeral=True,
        )
        return

    advanced_user_ids = await access_dao.fetch_user_ids_by_access_privilege("advanced")
    blocked_user_ids = await access_dao.fetch_user_ids_by_access_privilege("blocked")

    if target_user_id in advanced_user_ids and target_user_id in blocked_user_ids:
        await interaction.response.send_message(
            f"The user (ID: `{target_user_id}`) has the access privilege `advanced` and `blocked`",
            ephemeral=True,
        )
        return
    if target_user_id in advanced_user_ids:
        await interaction.response.send_message(
            f"The user (ID: `{target_user_id}`) has the access privilege `advanced`",
            ephemeral=True,
        )
        return
    if target_user_id in blocked_user_ids:
        await interaction.response.send_message(
            f"The user (ID: `{target_user_id}`) has the access privilege `blocked`",
            ephemeral=True,
        )
        return
    await interaction.response.send_message(
        f"The user (ID: `{target_user_id}`) does not have any access privilege",
        ephemeral=True,
    )


@client.tree.command(name="disable_access", description="Disable an access privilege for the user")
@is_authorized_server()  # type: ignore # noqa: F405
@is_admin_user()  # type: ignore # noqa: F405
async def disable_access_command(interaction: Interaction, user: User) -> None:
    """Disable access type for a Discord user.

    Parameters
    ----------
    interaction : Interaction
        The Discord interaction context.
    user : User
        The target Discord user to disable access for.

    Notes
    -----
    This function disables 'advanced' or 'blocked' access privilege for the specified user.
    """
    target_user_id = user.id
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used in a guild",
            ephemeral=True,
        )
        return

    target_user = interaction.guild.get_member(target_user_id)
    if target_user is None:
        await interaction.response.send_message(
            "The user does not exist in the guild",
            ephemeral=True,
        )
        return

    options = [
        SelectOption(label="advanced", value="advanced"),
        SelectOption(label="blocked", value="blocked"),
    ]

    select = AccessDisableSelector(user_id=target_user_id, options=options)
    view = View()
    view.add_item(select)

    await interaction.response.send_message(
        "Select an access privilege to disable for the user",
        view=view,
        ephemeral=True,
    )
