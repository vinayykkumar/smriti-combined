import cloudinary
import cloudinary.uploader
from app.config.settings import settings

# Initialize Cloudinary
if settings.CLOUDINARY_CLOUD_NAME:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET
    )

async def upload_file(file_content: bytes, filename: str, folder: str = "smriti/documents") -> dict:
    """
    Upload a file to Cloudinary
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        folder: Cloudinary folder path
        
    Returns:
        dict with url and public_id
    """
    if not settings.CLOUDINARY_CLOUD_NAME:
        raise ValueError("Cloudinary is not configured. Please add credentials to .env")
    
    result = cloudinary.uploader.upload(
        file_content,
        folder=folder,
        resource_type="auto",  # Auto-detect file type
        use_filename=True,
        unique_filename=True,
        filename_override=filename
    )
    
    return {
        "url": result.get("secure_url"),
        "public_id": result.get("public_id"),
        "format": result.get("format")
    }

async def delete_file(public_id: str) -> bool:
    """Delete a file from Cloudinary"""
    if not settings.CLOUDINARY_CLOUD_NAME:
        return False
        
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception:
        return False
