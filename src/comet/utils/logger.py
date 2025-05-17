import logging
import re
from logging import Logger, LogRecord
from pathlib import Path


class SensitiveDataFilter(logging.Filter):
    """Filter sensitive data from log messages for security reasons.

    This filter masks the values of variables ending with '_SYSTEM'.
    """

    def filter(self, record: LogRecord) -> bool:
        """Filter log records to mask sensitive data.

        Parameters
        ----------
        record : LogRecord
            The log record to be filtered.

        Returns
        -------
        bool
            Always returns True to process the record.
        """
        if isinstance(record.msg, str):
            # Replace values of variables ending with _SYSTEM with "*****"
            record.msg = re.sub(r"[A-Za-z0-9_]+_SYSTEM\s*=\s*[^\s,;]+", r"\g<0>=*****", record.msg)
            # Handle pattern where variable is already expanded
            record.msg = re.sub(r"[A-Za-z0-9_]+_SYSTEM:\s*[^\s,;]+", r"\g<0>:*****", record.msg)

        return True


def setup_logger(log_level: str) -> Logger:
    """Set up a logger for the calling file.

    Parameters
    ----------
    log_level : str
        The logging level specified as a string (case-insensitive).
        Valid string values:
        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - CRITICAL

    Returns
    -------
    Logger
        Configured logger instance with the specified log level and
        handlers for both file and console output.

    Raises
    ------
    TypeError
        If the provided log level is not a valid string value.

    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        msg = f"Invalid log level: {log_level}"
        raise TypeError(msg)

    log_file = "./logs/comet.log"

    # create log folder if not exists
    Path("./logs").mkdir(exist_ok=True)

    file_handler = logging.FileHandler(log_file)
    stream_handler = logging.StreamHandler()

    logging.basicConfig(
        level=numeric_level,
        # Format: [2025-01-27 00:13:26 - <filename>:102 - DEBUG] <message>
        format="[%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s] %(message)s",
        handlers=[
            file_handler,  # output logs to a .log
            stream_handler,  # output logs to console
        ],
    )

    logger = logging.getLogger(__name__)

    # Filter sensitive data
    sensitive_filter = SensitiveDataFilter()
    logger.addFilter(sensitive_filter)

    return logger
