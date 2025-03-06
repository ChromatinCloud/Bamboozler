# logging_config.py

import logging
import sys

# Create a named logger for BamBoozler
LOGGER_NAME = "bamboozler"
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)

# Ensure we only add handlers once (prevent duplication on import)
if not logger.handlers:
    # Format
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    # Stream handler (to stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

def get_logger():
    """
    Returns the bamboozler logger instance, ensuring it's configured once.
    """
    return logger

