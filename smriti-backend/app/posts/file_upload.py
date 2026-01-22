"""
File upload handling for posts.
"""
from fastapi import UploadFile, HTTPException
from app.posts.schemas import ContentType
from app.utils.cloudinary import upload_file
from app.posts.validators import validate_image_file, validate_document_file
from typing import Optional, Dict, Any


async def handle_image_upload(image: UploadFile) -> Dict[str, Any]:
    """
    Handle image file upload.
    
    Args:
        image: Image file to upload
        
    Returns:
        Dictionary with image_url and image_public_id
        
    Raises:
        HTTPException: If upload fails
    """
    # Validate file
    file_content = await image.read()
    validate_image_file(image.filename, len(file_content))
    
    # Upload to Cloudinary
    try:
        upload_result = await upload_file(file_content, image.filename)
        return {
            "image_url": upload_result["url"],
            "image_public_id": upload_result["public_id"]
        }
    except ValueError as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Image upload failed: {str(e)}"}
        )


async def handle_document_upload(document: UploadFile) -> Dict[str, Any]:
    """
    Handle document file upload.
    
    Args:
        document: Document file to upload
        
    Returns:
        Dictionary with document_url, document_type, and document_public_id
        
    Raises:
        HTTPException: If upload fails
    """
    # Validate file
    file_content = await document.read()
    validate_document_file(document.filename, len(file_content))
    
    # Upload to Cloudinary
    try:
        upload_result = await upload_file(file_content, document.filename)
        return {
            "document_url": upload_result["url"],
            "document_type": upload_result["format"],
            "document_public_id": upload_result["public_id"]
        }
    except ValueError as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"File upload failed: {str(e)}"}
        )


async def process_post_uploads(
    content_type: ContentType,
    image: Optional[UploadFile] = None,
    document: Optional[UploadFile] = None
) -> Dict[str, Any]:
    """
    Process file uploads for a post based on content type.
    
    Args:
        content_type: Type of post content
        image: Optional image file
        document: Optional document file
        
    Returns:
        Dictionary with upload results
    """
    result = {
        "image_url": None,
        "image_public_id": None,
        "document_url": None,
        "document_type": None,
        "document_public_id": None
    }
    
    if content_type == ContentType.image and image:
        image_data = await handle_image_upload(image)
        result.update(image_data)
    
    if content_type == ContentType.document and document:
        doc_data = await handle_document_upload(document)
        result.update(doc_data)
    
    return result
