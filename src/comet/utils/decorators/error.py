import functools
from collections.abc import Callable
from typing import Any

from src.comet._cli import parse_args_and_setup_logging
from src.comet.adapters.response import ResponseResult, ResponseStatus

logger = parse_args_and_setup_logging()


def handle_ai_service_errors(func: Callable[..., ResponseResult]) -> Callable[..., ResponseResult]:
    """Handle errors from AI service functions.

    Catch all exceptions and return the appropriate ResponseResult.

    Parameters
    ----------
    func : Callable
        The function to decorate

    Returns
    -------
    Callable
        The wrapped function
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> ResponseResult:  # noqa: ANN401
        try:
            return await func(*args, **kwargs)
        except Exception as err:
            error_type = err.__class__.__name__

            # Generate a custom message based on the error type
            if error_type in ["APIConnectionError", "APITimeoutError", "BadRequestError"]:
                msg = f"Failed to generate text: {err!s}"
            elif error_type == "InternalServerError":
                msg = f"InternalServerError has occurred: {err!s}"
            else:
                msg = f"Unexpected error has occurred: {err!s}"

            logger.exception(msg)
            return ResponseResult(status=ResponseStatus.ERROR, result=None)

    return wrapper
