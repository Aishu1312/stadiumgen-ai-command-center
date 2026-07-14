import time
from functools import wraps
from typing import Callable, Any
from utils.logging_utils import get_logger

logger = get_logger(__name__)

def track_time(func: Callable) -> Callable:
    """Decorator to measure and log execution time of a function."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            elapsed = end_time - start_time
            logger.info(f"Execution time for {func.__name__}: {elapsed:.3f} seconds")
    return wrapper
