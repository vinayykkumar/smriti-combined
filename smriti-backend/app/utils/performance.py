"""
Performance monitoring utilities.
"""
import time
from functools import wraps
from typing import Callable, Any
from app.utils.logger import get_logger

logger = get_logger("performance")


def measure_time(func: Callable) -> Callable:
    """
    Decorator to measure function execution time.
    
    Usage:
        @measure_time
        def my_function():
            ...
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} took {duration:.3f}s")
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} took {duration:.3f}s")
    
    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


class Timer:
    """
    Context manager for timing code blocks.
    
    Usage:
        with Timer("operation"):
            # code to time
    """
    
    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        logger.debug(f"{self.name} took {duration:.3f}s")
