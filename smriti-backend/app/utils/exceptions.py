"""
Custom exception classes for better error handling
"""

class AppException(Exception):
    """Base exception for all application errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ResourceNotFoundError(AppException):
    """Raised when a requested resource is not found"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class UnauthorizedError(AppException):
    """Raised when user is not authorized to perform an action"""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status_code=403)

class ValidationError(AppException):
    """Raised when input validation fails"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class ConflictError(AppException):
    """Raised when there's a conflict (e.g., duplicate username)"""
    def __init__(self, message: str):
        super().__init__(message, status_code=409)

class AuthenticationError(AppException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)
