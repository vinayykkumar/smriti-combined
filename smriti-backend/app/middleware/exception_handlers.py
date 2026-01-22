"""
Exception handlers for FastAPI application.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.utils.response_formatter import error_response
from app.utils.logger import log_error


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for HTTPException to return API design format.
    
    Args:
        request: FastAPI request object
        exc: HTTPException instance
        
    Returns:
        JSONResponse with standardized format
    """
    # If detail is already a dict with our format, use it
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    # Otherwise use error_response formatter
    return error_response(
        message=str(exc.detail),
        status_code=exc.status_code
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Convert validation errors (422) to 400 with custom message.
    
    Args:
        request: FastAPI request object
        exc: RequestValidationError instance
        
    Returns:
        JSONResponse with error message
    """
    errors = exc.errors()
    
    # Extract field name and create custom message
    if errors:
        first_error = errors[0]
        field = first_error.get("loc", [])[-1] if first_error.get("loc") else "field"
        error_type = first_error.get("type", "")
        error_msg_raw = first_error.get("msg", "")
        
        # Custom messages for common validation errors
        if field == "password" and ("min_length" in error_type or "string_too_short" in error_type or "at least 6" in error_msg_raw):
            error_msg = "Password must be at least 6 characters long"
        elif field == "username" and ("min_length" in error_type or "string_too_short" in error_type or "at least 3" in error_msg_raw):
            error_msg = "Username must be at least 3 characters long"
        elif field == "password" and "missing" in error_type:
            error_msg = "Password is required"
        elif field == "username" and "missing" in error_type:
            error_msg = "Username is required"
        else:
            # Use default message for other validation errors
            error_msg = error_msg_raw if error_msg_raw else "Invalid input"
    else:
        error_msg = "Invalid input"
    
    return error_response(
        message=error_msg,
        status_code=status.HTTP_400_BAD_REQUEST
    )


async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    
    Args:
        request: FastAPI request object
        exc: Exception instance
        
    Returns:
        JSONResponse with error message
    """
    # Log the error
    log_error(exc, context=f"Unhandled exception in {request.url.path}")
    
    return error_response(
        message="Something went wrong on the server. Please try again.",
        status_code=500
    )
