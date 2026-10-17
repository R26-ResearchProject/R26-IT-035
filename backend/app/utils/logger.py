# logger.py
# Sets up logging for the entire application
# Every service uses this to log messages

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a logger with the given name.
    Each service passes its own __name__ to get
    a logger specific to that file.

    Usage in other files:
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Something happened")
        logger.error("Something went wrong")
    """

    # Create logger with the given name
    logger = logging.getLogger(name)

    # Only add handler if logger has none
    # This prevents duplicate log messages
    if not logger.handlers:

        # Set log level — DEBUG shows everything
        logger.setLevel(logging.DEBUG)

        # Create handler that prints to terminal
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        # Format: time — file name — level — message
        formatter = logging.Formatter(
            "%(asctime)s — %(name)s — %(levelname)s — %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger