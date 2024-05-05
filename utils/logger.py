# utils/logger.py

import logging

def configure_logger(name):
    """
    Configure and return a logger with the given name.
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # Set the logging level

    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add formatter to ch
    ch.setFormatter(formatter)

    # Add ch to logger
    if not logger.handlers:  # Avoid adding multiple handlers if already present
        logger.addHandler(ch)

    return logger
