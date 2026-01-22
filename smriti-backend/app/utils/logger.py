"""
Logging utilities for Smriti Backend.
"""
import logging
from typing import Optional
from app.config.logging_config import setup_logging


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (defaults to module name)
        
    Returns:
        Logger instance
    """
    if name is None:
        name = __name__
    
    return logging.getLogger(name)


def log_request(method: str, path: str, status_code: int, duration: float):
    """
    Log HTTP request details.
    
    Args:
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration: Request duration in seconds
    """
    logger = get_logger("request")
    logger.info(
        f"{method} {path} - {status_code} - {duration:.3f}s"
    )


def log_error(error: Exception, context: Optional[str] = None):
    """
    Log error with context.
    
    Args:
        error: Exception object
        context: Additional context string
    """
    logger = get_logger("error")
    error_msg = f"{type(error).__name__}: {str(error)}"
    
    if context:
        error_msg = f"{context} - {error_msg}"
    
    logger.error(error_msg, exc_info=True)
