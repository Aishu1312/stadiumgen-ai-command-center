import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured structured logger.
    Keeps logs developer-focused and does not expose them to users.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.propagate = False
    return logger
