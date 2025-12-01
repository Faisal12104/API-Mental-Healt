from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from app.schemas.forum_post import ForumPostCreate, ForumPostResponse, ForumPostUpdate, PostReportCreate
from app.utils.database import (
    create_forum_post, get_forum_posts, get_forum_post_by_id, update_forum_post, delete_forum_post,
    like_post, unlike_post, is_post_liked, create_forum_report, is_room_member, update_room_activity
)
from app.models.forum_post import ForumPost, PostLike
from app.models.user import User
from app.auth.jwt_handler import verify_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/forum", tags=["Forum Posts"])

# Dependency untuk mendapatkan current user
async def get_current_user(token: str = Depends(verify_token)):
    from app.utils.database import get_user_by_id
    user_data = get_user_by_id(token.user_id)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return User.from_dict(user_data)

@router.post("/rooms/{room_id}/posts", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_forum_post_endpoint(
    room_id: str,
    post_data: ForumPostCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new post in forum room
    """
    try:
        logger.info(f"🔍 Creating post in room: {room_id}")
        
        # Check if user has joined the room
        if not is_room_member(room_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Must be a member to post in this room"
            )
        
        post_dict = post_data.dict()
        post = ForumPost.from_dict(post_dict)
        post.author_id = current_user.id
        
        # Handle anonymous posting
        if post.is_anonymous:
            post.author_id = "anonymous"  # For display purposes
        
        post_dict_for_db = post.to_dict()
        post_dict_for_db['author_id'] = current_user.id  # Keep real author_id in DB
        
        result = create_forum_post(post_dict_for_db)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create post"
            )
        
        # Update room activity
        update_room_activity(room_id)
        
        # Prepare response
        response_post = ForumPostResponse(**post_dict_for_db)
        response_post.author_name = "Anonymous User" if post.is_anonymous else current_user.name
        response_post.author_avatar = None if post.is_anonymous else current_user.avatar
        response_post.is_liked = False
        
        logger.info(f"✅ Post created in room: {room_id}")
        
        return {
            "success": True,
            "data": {
                "post": response_post
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/rooms/{room_id}/posts", response_model=dict)
async def get_forum_posts_endpoint(
    room_id: str,
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort: str = Query("newest", description="Sort by: newest or popular")
):
    """
    Get posts in forum room
    """
    try:
        logger.info(f"🔍 Getting posts from room: {room_id}")
        
        # Check if user has joined the room
        if not is_room_member(room_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Must be a member to view posts in this room"
            )
        
        posts_data = get_forum_posts(room_id, page, limit, sort)
        
        # Prepare response with like status
        posts = []
        for post_data in posts_data:
            post = ForumPostResponse(**ForumPost.from_dict(post_data).to_dict())
            
            # Handle anonymous authors
            if post.is_anonymous:
                post.author_name = "Anonymous User"
                post.author_avatar = None
            else:
                post.author_name = post_data.get('author_name', 'User')
                post.author_avatar = post_data.get('author_avatar')
            
            post.is_liked = is_post_liked(post.id, current_user.id) is not None
            posts.append(post)
        
        logger.info(f"✅ Retrieved {len(posts)} posts from room: {room_id}")
        
        return {
            "success": True,
            "data": {
                "posts": posts,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(posts)
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting posts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/posts/{post_id}/like", response_model=dict)
async def like_post_endpoint(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Like a forum post
    """
    try:
        logger.info(f"🔍 User {current_user.email} liking post: {post_id}")
        
        # Check if post exists
        post_data = get_forum_post_by_id(post_id)
        if not post_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check if user has joined the room
        room_id = post_data['room_id']
        if not is_room_member(room_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Must be a member to interact with posts in this room"
            )
        
        # Check if already liked
        if is_post_liked(post_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post already liked"
            )
        
        # Like post
        like_data = {
            'post_id': post_id,
            'user_id': current_user.id
        }
        result = like_post(like_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to like post"
            )
        
        logger.info(f"✅ User {current_user.email} liked post: {post_id}")
        
        return {
            "success": True,
            "message": "Post liked successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error liking post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/posts/{post_id}/like", response_model=dict)
async def unlike_post_endpoint(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Unlike a forum post
    """
    try:
        logger.info(f"🔍 User {current_user.email} unliking post: {post_id}")
        
        # Check if post exists
        post_data = get_forum_post_by_id(post_id)
        if not post_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check if actually liked
        if not is_post_liked(post_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post not liked"
            )
        
        # Unlike post
        result = unlike_post(post_id, current_user.id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to unlike post"
            )
        
        logger.info(f"✅ User {current_user.email} unliked post: {post_id}")
        
        return {
            "success": True,
            "message": "Post unliked successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error unliking post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/posts/{post_id}/report", response_model=dict)
async def report_post_endpoint(
    post_id: str,
    report_data: PostReportCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Report a forum post
    """
    try:
        logger.info(f"🔍 User {current_user.email} reporting post: {post_id}")
        
        # Check if post exists
        post_data = get_forum_post_by_id(post_id)
        if not post_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Create report
        report_dict = report_data.dict()
        report_dict['post_id'] = post_id
        report_dict['reporter_id'] = current_user.id
        
        result = create_forum_report(report_dict)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to report post"
            )
        
        logger.info(f"✅ User {current_user.email} reported post: {post_id}")
        
        return {
            "success": True,
            "message": "Post reported successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error reporting post: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/trending", response_model=dict)
async def get_trending_posts_endpoint(
    current_user: User = Depends(get_current_user),
    period: str = Query("week", description="Period: day, week, month"),
    limit: int = Query(10, ge=1, le=50, description="Number of posts")
):
    """
    Get trending posts across all rooms
    """
    try:
        logger.info(f"🔍 Getting trending posts - period: {period}")
        
        posts_data = get_trending_posts(period, limit)
        
        # Prepare response with like status
        posts = []
        for post_data in posts_data:
            post = ForumPostResponse(**ForumPost.from_dict(post_data).to_dict())
            
            # Handle anonymous authors
            if post.is_anonymous:
                post.author_name = "Anonymous User"
                post.author_avatar = None
            else:
                post.author_name = post_data.get('author_name', 'User')
                post.author_avatar = post_data.get('author_avatar')
            
            post.is_liked = is_post_liked(post.id, current_user.id) is not None
            posts.append(post)
        
        logger.info(f"✅ Retrieved {len(posts)} trending posts")
        
        return {
            "success": True,
            "data": posts
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting trending posts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )