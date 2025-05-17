from enum import Enum

from discord import Colour, Embed, Thread
from pydantic import BaseModel

from src.comet.config.env import MAX_CHARS_PER_MESSAGE


class ResponseStatus(Enum):
    """Enumeration of possible response statuses from AI generation.

    Attributes
    ----------
    SUCCESS : int
        Indicates the response was generated successfully.
    ERROR : int
        Indicates an error occurred during response generation.
    MODERATION_FLAGGED : int
        Indicates the response was flagged by the moderation system.
    """

    SUCCESS = 0
    ERROR = 1
    MODERATION_FLAGGED = 2


class ResponseResult(BaseModel):
    """Container for AI response results.

    Parameters
    ----------
    status : ResponseStatus
        The status of the response generation process.
    result : str | None
        The generated text response, or None if generation failed.
    """

    status: ResponseStatus
    result: str | None


def _split_into_shorter_messages(message: str) -> list[str]:
    """Split a long message into multiple shorter messages.

    Parameters
    ----------
    message : str
        The long message string that needs to be split.

    Returns
    -------
    list[str]
        A list of message segments, each within the character limit.
    """
    return [
        message[i : i + MAX_CHARS_PER_MESSAGE]
        for i in range(0, len(message), MAX_CHARS_PER_MESSAGE)
    ]


async def send_response_result(thread: Thread, result: ResponseResult) -> None:
    """Send the response result to a Discord thread.

    Parameters
    ----------
    thread : Thread
        The Discord thread where the response result will be sent.
    result : ResponseResult
        The result of the response process, containing status,
        generated message, and status information.
    """
    status = result.status
    if status == ResponseStatus.SUCCESS:
        if not result.result:
            await thread.send(
                embed=Embed(
                    description="**WARNING** - The assistant's response is empty.",
                    color=Colour.yellow(),
                ),
            )
        else:
            shorter_response = _split_into_shorter_messages(result.result)
            for res in shorter_response:
                await thread.send(res)
    elif status == ResponseStatus.ERROR:
        await thread.send(
            embed=Embed(
                description="**ERROR** - Response generation failed.",
                color=Colour.red(),
            ),
        )
