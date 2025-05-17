import argparse
from logging import Logger
from typing import cast

from src.comet.utils.logger import setup_logger


def parse_args_and_setup_logging() -> Logger:
    """Parse command line arguments and set up logging configuration.

    This function initializes argument parsing for command line options
    and sets up the logging configuration for the application.

    Returns
    -------
    logging.Logger
        Configured logger instance with the log level specified
        by the --log command line argument.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log",
        default="INFO",
    )

    args = parser.parse_args()
    # Due to mypy not correctly recognizing the type, an explicit cast is required
    return cast("Logger", setup_logger(args.log))
