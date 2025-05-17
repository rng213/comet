from discord import (
    Interaction,
    TextStyle,
)
from discord.ui import Modal, TextInput

from src.comet._cli import parse_args_and_setup_logging
from src.comet.adapters.chat import ChatMessage
from src.comet.ai.models.claude_model import ClaudeModelParams
from src.comet.ai.models.storage import ModelParamsStore
from src.comet.ai.services.completion import generate_anthropic_response
from src.comet.config.env import (
    CLAUDE_DEFAULT_MAX_TOKENS,
    CLAUDE_DEFAULT_TEMPERATURE,
    CLAUDE_DEFAULT_TOP_P,
    FIXPY_MODEL,
)
from src.comet.config.yml import FIXPY_SYSTEM
from src.comet.db.dao.access_privilege_dao import AccessPrivilegeDAO
from src.comet.discord.client import BotClient
from src.comet.utils.decorators import *

access_dao = AccessPrivilegeDAO()
client = BotClient.get_instance()
logger = parse_args_and_setup_logging()
model_params = ModelParamsStore()


class CodeModal(Modal):
    """Modal for entering Python code to fix."""

    code_input: TextInput

    def __init__(self, temperature: float, top_p: float) -> None:
        """Initialize the code modal with AI parameters.

        Parameters
        ----------
        temperature : float
            The temperature parameter for Claude.
        top_p : float
            The top_p parameter for Claude.
        """
        super().__init__(title="Fix Python Code")

        self.code_input = TextInput(
            label="Python Code",
            style=TextStyle.long,
            placeholder="Enter the Python code you want to fix",
            required=True,
        )
        self.add_item(self.code_input)

        # Save parameters
        self.temperature = temperature
        self.top_p = top_p

    async def on_submit(self, interaction: Interaction) -> None:
        """Handle the submission of the modal.

        Parameters
        ----------
        interaction : Interaction
            The interaction object from Discord.
        """
        await interaction.response.defer(thinking=True)

        try:
            code = self.code_input.value

            if FIXPY_MODEL is None:
                await interaction.followup.send(
                    "*ERROR* No available model. Please contact the owner.",
                    ephemeral=True,
                )
                return

            params = ClaudeModelParams(
                model=FIXPY_MODEL,
                max_tokens=CLAUDE_DEFAULT_MAX_TOKENS,
                temperature=self.temperature,
                top_p=self.top_p,
            )

            message = [ChatMessage(role="user", content=code)]

            response_result = await generate_anthropic_response(
                system_prompt=FIXPY_SYSTEM,
                prompt=message,
                model_params=params,
            )

            await interaction.followup.send(
                f"{response_result.result}",
                ephemeral=True,
            )

        except Exception as err:
            msg = f"Error processing fixpy request: {err!s}"
            logger.exception(msg)
            await interaction.followup.send(
                "**ERROR** - Error occurred while fixing the code.",
                ephemeral=True,
            )


@client.tree.command(name="fixpy", description="Detect and fix bugs in Python code")
@is_authorized_server()  # type: ignore # noqa: F405
@is_not_blocked_user()  # type: ignore # noqa: F405
async def fix_command(
    interaction: Interaction,
    temperature: float = CLAUDE_DEFAULT_TEMPERATURE,
    top_p: float = CLAUDE_DEFAULT_TOP_P,
) -> None:
    """Detect and fix bugs in Python code.

    Parameters
    ----------
    interaction : Interaction
        The interaction instance.
    temperature : float, optional
        The temperature parameter for Claude, by default CLAUDE_DEFAULT_TEMPERATURE.
    top_p : float, optional
        The top-p parameter for Claude, by default CLAUDE_DEFAULT_TOP_P.
    """
    try:
        user = interaction.user
        logger.info("User ( %s ) executed 'fixpy' command", user)

        if FIXPY_MODEL is None:
            await interaction.response.send_message(
                "**ERROR** - No available model.",
                ephemeral=True,
            )
            return

        # Show the modal to input code
        modal = CodeModal(temperature=temperature, top_p=top_p)
        await interaction.response.send_modal(modal)

    except Exception as err:
        msg = f"Error showing fixpy modal: {err!s}"
        logger.exception(msg)
        await interaction.response.send_message(
            "**ERROR** - Error occurred while executing the command.",
            ephemeral=True,
        )
