"""
API-related constants.
"""

# API Version
API_VERSION = "v1"
API_PREFIX = "/api"

# Response Messages
SUCCESS_MESSAGES = {
    "CREATED": "Resource created successfully",
    "UPDATED": "Resource updated successfully",
    "DELETED": "Resource deleted successfully",
    "RETRIEVED": "Resource retrieved successfully",
}

# Pagination Defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
DEFAULT_SKIP = 0

# File Upload Limits
MAX_FILE_SIZE_MB = 10.0
ALLOWED_IMAGE_TYPES = ["jpg", "jpeg", "png", "gif", "webp"]
ALLOWED_DOCUMENT_TYPES = ["pdf", "doc", "docx"]
