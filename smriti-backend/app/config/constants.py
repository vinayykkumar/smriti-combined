"""
Application-wide constants and configuration values
"""

class FileUploadConfig:
    """File upload constraints and allowed types"""
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
    ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "doc", "docx", "txt"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
class PaginationConfig:
    """Default pagination values"""
    DEFAULT_SKIP = 0
    DEFAULT_LIMIT = 20
    MAX_LIMIT = 100
