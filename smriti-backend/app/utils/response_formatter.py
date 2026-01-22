"""
Response formatting utilities.
"""
from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200
) -> JSONResponse:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        
    Returns:
        JSONResponse with standardized format
    """
    response_data = {
        "success": True,
        "message": message
    }
    
    if data is not None:
        response_data["data"] = data
    
    return JSONResponse(content=response_data, status_code=status_code)


def error_response(
    message: str = "An error occurred",
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        details: Additional error details
        
    Returns:
        JSONResponse with standardized error format
    """
    response_data = {
        "success": False,
        "error": message
    }
    
    if details:
        response_data["details"] = details
    
    return JSONResponse(content=response_data, status_code=status_code)
