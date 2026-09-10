import logging
import os
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

load_dotenv()

_configured = False


def setup_logging():
    """Configures the 'bookstore' logger once per application run.
    Called from main.py before startup. Modules obtain child loggers
    via get_logger(__name__).
    """
    global _configured
    if _configured:
        return
    _configured = True

    log_file = os.getenv("LOG_FILE", "bookstore.log")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    logger = logging.getLogger("bookstore")
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Only warnings and higher go to the console, so as not to interfere with the standard
    # menu output via print() intended for the user.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def get_logger(name):
    """name is the __name__ of the calling module."""
    return logging.getLogger(f"bookstore.{name}")
