from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from src.comet.ai.models._types import ModelParamsType


class ModelParamsStore:
    """A singleton class for storing model parameters.

    This class implements the Singleton pattern to ensure only one instance
    exists throughout the application. It provides methods to store and
    retrieve model configuration parameters indexed by a key.
    """

    _instance = None
    params: dict

    def __new__(cls) -> Self:
        """Create a new instance of ModelParamsStore or return the existing one.

        This method implements the Singleton pattern.

        Returns
        -------
        Self
            The singleton instance of ModelParamsStore.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.params = {}
        return cls._instance

    def set_model_params(self, key: int, config: ModelParamsType) -> None:
        """Store model parameters under the specified key.

        Parameters
        ----------
        key : int
            The unique identifier for the model parameters.
        config : ModelParamsType
            The parameters to be stored, which must be matched to the ModelParamsType.
            This type contains the model configuration.
        """
        self.params[key] = config

    def get_model_params(self, key: int) -> Any | None:  # noqa: ANN401
        """Retrieve model parameters associated with the specified key.

        Parameters
        ----------
        key : int
            The unique identifier for the model parameters.

        Returns
        -------
        Any or None
            The model parameters if found, None otherwise.
        """
        return self.params.get(key)
