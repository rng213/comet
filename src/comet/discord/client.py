from discord import Client, Intents, app_commands

from src.comet._cli import parse_args_and_setup_logging

logger = parse_args_and_setup_logging()

intents = Intents.default()
intents.message_content = True
intents.members = True


class BotClient(Client):
    """A singleton bot client for Discord applications.

    Attributes
    ----------
    _instance : BotClient
        The singleton instance of the BotClient class.
    tree : app_commands.CommandTree
        The command tree for registering and managing slash commands.
    """

    _instance: "BotClient"
    tree: app_commands.CommandTree

    def __init__(self) -> None:
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    @classmethod
    def get_instance(cls) -> "BotClient":
        """Get the singleton instance of the BotClient class.

        Returns
        -------
        BotClient
            The instance of the BotClient class.
        """
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    async def setup_hook(self) -> None:
        """Set up the bot before connecting to the Discord gateway."""
        synced_cmds = await self.tree.sync()
        logger.info("Setup hook completed")
        logger.info("Synced %d commands", len(synced_cmds))

    async def on_ready(self) -> None:
        """Handle the bot's ready event."""
        logger.info("%s is ready!!", self.user)
        for cmd in self.tree.walk_commands():
            logger.info("Command Name: %s", cmd.name)

    async def cleanup_hook(self) -> None:
        """Clean up resources when the bot is shutting down."""
        logger.info("Start cleanup ...")
