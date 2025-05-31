from __future__ import annotations

from typing import TYPE_CHECKING

from src.comet.ai.models._base import ModelParamsBase

if TYPE_CHECKING:
    from discord import app_commands


class ClaudeModelParams(ModelParamsBase):
    """Parameters for Claude model.

    Parameters
    ----------
    model : app_commands.Choice[int] | str
        The model to use.
    max_tokens : int
        The maximum number of tokens that can be generated in the
        completion. Must be between 1 and CLAUDE_DEFAULT_MAX_TOKENS.
    temperature : float
        The temperature parameter for sampling, controlling randomness.
        Must be between 0.0 and CLAUDE_DEFAULT_TEMPERATURE.
    top_p : float
        The top-p sampling parameter, controlling diversity. Must be
        between 0.0 and BASE_TOP_P.
        This parameter is inherited from ModelParamsBase.
    """

    @property
    def model(self) -> app_commands.Choice[int] | str:
        """Get the model parameter."""
        return self._model

    @model.setter
    def model(self, value: app_commands.Choice[int] | str) -> None:
        """Set and validate model."""
        self._model = value

    @property
    def max_tokens(self) -> int:
        """Get the max_tokens parameter."""
        return self._max_tokens

    @max_tokens.setter
    def max_tokens(self, value: int) -> None:
        """Set and validate max_tokens."""
        if not 1 <= value <= 8192:  # noqa: PLR2004
            msg = "The max_tokens must be between 1 and 8192."
            raise ValueError(msg)
        self._max_tokens = value

    @property
    def temperature(self) -> float:
        """Get the temperature parameter."""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Set and validate temperature."""
        if not (0.0 <= value <= 1.0):
            msg = "Claude's temperature must be between 0.0 and 1.0."
            raise ValueError(msg)
        self._temperature = value

    @property
    def top_p(self) -> float:
        """Get the top_p parameter."""
        return self._top_p

    @top_p.setter
    def top_p(self, value: float) -> None:
        """Set and validate top_p."""
        self.validate_top_p(value)
        self._top_p = value
