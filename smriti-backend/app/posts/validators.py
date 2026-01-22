"""
Post validation utilities.
"""
from fastapi import HTTPException
from app.posts.schemas import ContentType
from typing import Optional
from app.utils.file_helpers import is_allowed_file_type, validate_file_size
from app.constants.api import ALLOWED_IMAGE_TYPES, ALLOWED_DOCUMENT_TYPES, MAX_FILE_SIZE_MB


def validate_post_content(
    content_type: ContentType,
    text_content: Optional[str] = None,
    link_url: Optional[str] = None,
    image: Optional[object] = None,
    document: Optional[object] = None
):
    """
    Validate post content based on content type.
    
    Args:
        content_type: Type of content
        text_content: Text content for note posts
        link_url: URL for link posts
        image: Image file for image posts
        document: Document file for document posts
        
    Raises:
        HTTPException: If validation fails
    """
    if content_type == ContentType.note and not text_content:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "text_content is required for note posts"}
        )
    
    if content_type == ContentType.link and not link_url:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "link_url is required for link posts"}
        )
    
    if content_type == ContentType.image and not image:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "image file is required for image posts"}
        )
    
    if content_type == ContentType.document and not document:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "document file is required for document posts"}
        )


def validate_image_file(filename: str, file_size: int):
    """
    Validate image file.
    
    Args:
        filename: Image filename
        file_size: File size in bytes
        
    Raises:
        HTTPException: If validation fails
    """
    if not is_allowed_file_type(filename, ALLOWED_IMAGE_TYPES):
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": f"Invalid image type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"}
        )
    
    is_valid, error_msg = validate_file_size(file_size, MAX_FILE_SIZE_MB)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": error_msg}
        )


def validate_document_file(filename: str, file_size: int):
    """
    Validate document file.
    
    Args:
        filename: Document filename
        file_size: File size in bytes
        
    Raises:
        HTTPException: If validation fails
    """
    if not is_allowed_file_type(filename, ALLOWED_DOCUMENT_TYPES):
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": f"Invalid file type. Allowed: {', '.join(ALLOWED_DOCUMENT_TYPES)}"}
        )
    
    is_valid, error_msg = validate_file_size(file_size, MAX_FILE_SIZE_MB)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": error_msg}
        )
