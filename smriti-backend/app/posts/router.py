from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from typing import Optional
from app.database.connection import get_database
from app.posts.schemas import PostResponse, ContentType
from app.auth.schemas import UserResponse
from app.auth.dependencies import get_current_user
from app.utils.response_formatter import success_response
from app.utils.date_helpers import get_current_timestamp
from app.posts import service
from app.posts.validators import validate_post_content
from app.posts.file_upload import process_post_uploads

router = APIRouter()

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
    
    # Validate post content
    validate_post_content(content_type, text_content, link_url, image, document)
    
    # Process file uploads
    upload_data = await process_post_uploads(content_type, image, document)
    
    # Create post document
    post_dict = {
        "content_type": content_type,
        "title": title,
        "text_content": text_content,
        "link_url": link_url,
        **upload_data,
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
    
    return success_response(
        data={
            "posts": [
                PostResponse(**{**post, "_id": str(post["_id"])}) 
                for post in posts
            ]
        },
        message="Posts retrieved successfully"
    )

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
