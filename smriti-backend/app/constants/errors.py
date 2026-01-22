"""
Error constants and messages.
"""

# HTTP Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_500_INTERNAL_SERVER_ERROR = 500

# Error Messages
ERROR_MESSAGES = {
    "NETWORK_ERROR": "Network error occurred",
    "VALIDATION_ERROR": "Validation error",
    "UNAUTHORIZED": "Unauthorized access",
    "NOT_FOUND": "Resource not found",
    "SERVER_ERROR": "Internal server error",
    "DATABASE_ERROR": "Database operation failed",
}

# Validation Messages
VALIDATION_MESSAGES = {
    "EMAIL_REQUIRED": "Email is required",
    "EMAIL_INVALID": "Invalid email format",
    "USERNAME_REQUIRED": "Username is required",
    "USERNAME_INVALID": "Invalid username format",
    "PASSWORD_REQUIRED": "Password is required",
    "PASSWORD_TOO_SHORT": "Password must be at least 6 characters",
}
