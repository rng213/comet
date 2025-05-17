from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import app_commands


class ModelParamsBase(ABC):
    """Base class for AI model parameters.

    This abstract class defines the common interface and
    validation logic for all AI model parameter classes.
    """

    def __init__(
        self,
        model: app_commands.Choice[int] | str,
        max_tokens: int,
        temperature: float,
        top_p: float,
    ) -> None:
        """Initialize model parameters.

        Parameters
        ----------
        model : app_commands.Choice[int] | str
            The model to use.
        max_tokens : int
            The maximum number of tokens to generate.
        temperature : float
            The sampling temperature.
        top_p : float
            The nucleus sampling parameter.
        """
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

    # Abstract method definitions for property overrides in child classes
    @property
    @abstractmethod
    def model(self) -> app_commands.Choice[int] | str:
        """Get the model parameter."""

    @model.setter
    @abstractmethod
    def model(self, value: app_commands.Choice[int] | str) -> None:
        """Set and validate model."""

    @property
    @abstractmethod
    def max_tokens(self) -> int:
        """Get the max_tokens parameter."""

    @max_tokens.setter
    @abstractmethod
    def max_tokens(self, value: int) -> None:
        """Set and validate max_tokens."""

    @property
    @abstractmethod
    def temperature(self) -> float:
        """Get the temperature parameter."""

    @temperature.setter
    @abstractmethod
    def temperature(self, value: float) -> None:
        """Set and validate temperature."""

    @property
    @abstractmethod
    def top_p(self) -> float:
        """Get the top_p parameter."""

    @top_p.setter
    @abstractmethod
    def top_p(self, value: float) -> None:
        """Set and validate the top-p value to use for the model."""

    def validate_top_p(self, value: float) -> None:
        if not (0.0 <= value <= 1.0):
            msg = "Top-p must be between 0.0 and 1.0."
            raise ValueError(msg)
