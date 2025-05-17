from __future__ import annotations

from discord import Message as DiscordMessage
from discord import MessageType
from pydantic import BaseModel

from src.comet.config.env import BOT_NAME


class ChatMessage(BaseModel):
    """Represents a single chat message with a role and content.

    Attributes
    ----------
    role : str
        The role of the message sender, e.g., 'developer', 'assistant', or 'user'.
    content : str | None
        The content of the message. Defaults to None.
    """

    role: str
    content: str | None = None

    def format_message(self) -> dict[str, str]:
        """Represent a single chat message with a role and content.

        Returns
        -------
        dict
            A dictionary with 'role' and 'content' keys.
        """
        return {
            # If self.role matches BOT_NAME, return "assistant",
            # otherwise if self.role is "developer" or "assistant", use that value,
            # otherwise treat it as "user"
            "role": "assistant"
            if self.role == BOT_NAME
            else (self.role if self.role in ("developer", "assistant") else "user"),
            "content": self.content or "",
        }

    @classmethod
    async def from_discord_message(cls, message: DiscordMessage) -> ChatMessage | None:
        """Convert a DiscordMessage instance to a ChatMessage instance.

        Parameters
        ----------
        message : DiscordMessage
            A message from Discord, which may be a thread starter or a
            regular message.

        Returns
        -------
        ChatMessage | None
            A ChatMessage instance if the conversion is successful,
            otherwise None.

        Examples
        --------
        >>> discord_msg = ...  # Discord message object
        >>> chat_msg = await ChatMessage.from_discord_message(discord_msg)
        >>> if chat_msg:
        ...     print(chat_msg.format_message())
        """
        # Process thread starter message
        if (
            message.type == MessageType.thread_starter_message
            and message.reference is not None
            and message.reference.cached_message
            and message.reference.cached_message.embeds
            and message.reference.cached_message.embeds[0].fields
        ):
            field = message.reference.cached_message.embeds[0].fields[0]
            return cls(role=message.author.name, content=field.value)
        # Process regular message
        if message.content is not None:
            return cls(role=message.author.name, content=message.content)
        return None


class ChatHistory(BaseModel):
    """Manage a collection of chat messages.

    Attributes
    ----------
    messages : list[ChatMessage]
        A list of ChatMessage objects representing the chat history.
    """

    messages: list[ChatMessage]

    def render_message(self) -> list[dict[str, str]]:
        """Render the chat messages into a list of dictionaries.

        Returns
        -------
        list[dict[str, str]]
            A list where each dictionary represents a chat message with
            'role' and 'content' keys.
        """
        return [message.format_message() for message in self.messages]
