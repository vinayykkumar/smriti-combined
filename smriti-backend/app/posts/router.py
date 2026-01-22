from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from typing import Optional
from app.database.connection import get_database
from app.posts.schemas import PostResponse, ContentType
from app.auth.schemas import UserResponse
from app.auth.dependencies import get_current_user
from app.utils.cloudinary import upload_file
from app.utils.file_helpers import is_allowed_file_type, validate_file_size, get_file_extension
from app.utils.response_formatter import success_response, error_response
from app.utils.date_helpers import get_current_timestamp
from app.constants.api import ALLOWED_IMAGE_TYPES, ALLOWED_DOCUMENT_TYPES, MAX_FILE_SIZE_MB
from app.posts import service
from bson import ObjectId

router = APIRouter()

# Convert constants to sets for compatibility
ALLOWED_IMAGE_EXTENSIONS = set(ALLOWED_IMAGE_TYPES)
ALLOWED_DOCUMENT_EXTENSIONS = set(ALLOWED_DOCUMENT_TYPES)
MAX_FILE_SIZE = int(MAX_FILE_SIZE_MB * 1024 * 1024)  # Convert MB to bytes

@router.get("/", response_model=dict)
async def get_posts(
    skip: int = Query(0, ge=0, description="Number of posts to skip"),
    limit: int = Query(50, gt=0, le=100, description="Max posts to return"),
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all posts in chronological order (newest first)"""
    posts = await service.get_all_posts(db, skip, limit)
    
    return success_response(
        data={
            "count": len(posts),
            "posts": [
                PostResponse(**{**post, "_id": str(post["_id"])}) 
                for post in posts
            ]
        },
        message="Posts retrieved successfully"
    )

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_post(
    content_type: ContentType = Form(...),
    title: Optional[str] = Form(None),
    text_content: Optional[str] = Form(None),
    link_url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    document: Optional[UploadFile] = File(None),
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new post (note, link, image, or document)"""
    
    # Validation based on content type
    if content_type == ContentType.note and not text_content:
        raise HTTPException(status_code=400, detail="text_content is required for note posts")
    
    if content_type == ContentType.link and not link_url:
        raise HTTPException(status_code=400, detail="link_url is required for link posts")
    
    if content_type == ContentType.image and not image:
        raise HTTPException(status_code=400, detail="image file is required for image posts")
    
    if content_type == ContentType.document and not document:
        raise HTTPException(status_code=400, detail="document file is required for document posts")
    
    # Handle image upload
    image_url = None
    image_public_id = None
    
    if content_type == ContentType.image and image:
        # Validate file extension using utility
        if not is_allowed_file_type(image.filename, ALLOWED_IMAGE_TYPES):
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": f"Invalid image type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"}
            )
        
        # Validate file size using utility
        file_content = await image.read()
        is_valid, error_msg = validate_file_size(len(file_content), MAX_FILE_SIZE_MB)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": error_msg}
            )
        
        # Upload to Cloudinary
        try:
            upload_result = await upload_file(file_content, image.filename)
            image_url = upload_result["url"]
            image_public_id = upload_result["public_id"]
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
    
    # Handle document upload
    document_url = None
    document_type = None
    document_public_id = None
    
    if content_type == ContentType.document and document:
        # Validate file extension using utility
        if not is_allowed_file_type(document.filename, ALLOWED_DOCUMENT_TYPES):
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": f"Invalid file type. Allowed: {', '.join(ALLOWED_DOCUMENT_TYPES)}"}
            )
        
        # Validate file size using utility
        file_content = await document.read()
        is_valid, error_msg = validate_file_size(len(file_content), MAX_FILE_SIZE_MB)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": error_msg}
            )
        
        # Upload to Cloudinary
        try:
            upload_result = await upload_file(file_content, document.filename)
            document_url = upload_result["url"]
            document_type = upload_result["format"]
            document_public_id = upload_result["public_id"]  # Store for deletion
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    # Create post document
    post_dict = {
        "content_type": content_type,
        "title": title,
        "text_content": text_content,
        "link_url": link_url,
        "image_url": image_url,
        "image_public_id": image_public_id,
        "document_url": document_url,
        "document_type": document_type,
        "document_public_id": document_public_id,  # Store for deletion
        "author": {
            "user_id": str(current_user.id),
            "username": current_user.username
        },
        "created_at": get_current_timestamp()
    }
    
    created_post = await service.create_post_db(db, post_dict, current_user)
    
    return success_response(
        data={"post": PostResponse(**{**created_post, "_id": str(created_post["_id"])})},
        message="Post created successfully",
        status_code=status.HTTP_201_CREATED
    )

@router.get("/me", response_model=dict)
async def get_my_posts(
    skip: int = Query(0, ge=0, description="Number of posts to skip"),
    limit: int = Query(20, gt=0, le=100, description="Max posts to return"),
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all posts authored by the current authenticated user"""
    posts = await service.get_posts_by_user(db, str(current_user.id), skip, limit)
    
    return {
        "success": True,
        "status": "success",
        "results": len(posts),
        "data": {
            "posts": [
                PostResponse(**{**post, "_id": str(post["_id"])}) 
                for post in posts
            ]
        }
    }

@router.delete("/{post_id}", response_model=dict)
async def delete_post(
    post_id: str,
    db = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a post (author only)"""
    post = await service.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "Post not found"}
        )
        
    # Only author can delete
    if post["author"]["user_id"] != str(current_user.id):
        raise HTTPException(
            status_code=403,
            detail={"success": False, "error": "Not authorized to delete this post"}
        )
    
    # Delete file from Cloudinary if it exists
    if post.get("document_public_id"):
        try:
            from app.utils.cloudinary import delete_file
            await delete_file(post["document_public_id"])
        except Exception as e:
            # Log error but don't fail the deletion
            print(f"Failed to delete file from Cloudinary: {e}")
        
    await service.delete_post_db(db, post_id)
    
    return success_response(
        message="Post deleted successfully"
    )
