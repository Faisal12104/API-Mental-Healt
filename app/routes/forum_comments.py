from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from app.schemas.forum_comment import ForumCommentCreate, ForumCommentResponse, ForumCommentUpdate
from app.schemas.forum_post import PostReportCreate  # ADD THIS IMPORT
from app.utils.database import (
    create_forum_comment, get_forum_comments, get_forum_comment_by_id, 
    update_forum_comment, delete_forum_comment, like_comment, unlike_comment, 
    is_comment_liked, get_forum_post_by_id, is_room_member, create_forum_report
)
from app.models.forum_comment import ForumComment, CommentLike
from app.models.user import User
from app.auth.jwt_handler import verify_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/forum/posts/{post_id}/comments", tags=["Forum Comments"])

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

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_forum_comment_endpoint(
    post_id: str,
    comment_data: ForumCommentCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new comment on a forum post
    """
    try:
        logger.info(f"🔍 Creating comment on post: {post_id}")
        
        # Check if post exists and get room_id
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
                detail="Must be a member to comment on posts in this room"
            )
        
        comment_dict = comment_data.dict()
        comment = ForumComment.from_dict(comment_dict)
        comment.post_id = post_id
        comment.author_id = current_user.id
        
        # Handle anonymous commenting
        if comment.is_anonymous:
            comment.author_id = "anonymous"  # For display purposes
        
        comment_dict_for_db = comment.to_dict()
        comment_dict_for_db['author_id'] = current_user.id  # Keep real author_id in DB
        
        result = create_forum_comment(comment_dict_for_db)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create comment"
            )
        
        # Prepare response
        response_comment = ForumCommentResponse(**comment_dict_for_db)
        response_comment.author_name = "Anonymous User" if comment.is_anonymous else current_user.name
        response_comment.author_avatar = None if comment.is_anonymous else current_user.avatar
        response_comment.is_liked = False
        
        logger.info(f"✅ Comment created on post: {post_id}")
        
        return {
            "success": True,
            "data": {
                "comment": response_comment
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("", response_model=dict)
async def get_forum_comments_endpoint(
    post_id: str,
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Get comments on a forum post
    """
    try:
        logger.info(f"🔍 Getting comments for post: {post_id}")
        
        # Check if post exists and get room_id
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
                detail="Must be a member to view comments in this room"
            )
        
        comments_data = get_forum_comments(post_id, page, limit)
        
        # Prepare response with like status
        comments = []
        for comment_data in comments_data:
            comment = ForumCommentResponse(**ForumComment.from_dict(comment_data).to_dict())
            
            # Handle anonymous authors
            if comment.is_anonymous:
                comment.author_name = "Anonymous User"
                comment.author_avatar = None
            else:
                comment.author_name = comment_data.get('author_name', 'User')
                comment.author_avatar = comment_data.get('author_avatar')
            
            comment.is_liked = is_comment_liked(comment.id, current_user.id) is not None
            comments.append(comment)
        
        logger.info(f"✅ Retrieved {len(comments)} comments for post: {post_id}")
        
        return {
            "success": True,
            "data": {
                "comments": comments,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(comments)
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting comments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/{comment_id}/like", response_model=dict)
async def like_comment_endpoint(
    post_id: str,
    comment_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Like a forum comment
    """
    try:
        logger.info(f"🔍 User {current_user.email} liking comment: {comment_id}")
        
        # Check if comment exists
        comment_data = get_forum_comment_by_id(comment_id)
        if not comment_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Verify comment belongs to post
        if comment_data['post_id'] != post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment does not belong to this post"
            )
        
        # Check if post exists and get room_id
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
                detail="Must be a member to interact with comments in this room"
            )
        
        # Check if already liked
        if is_comment_liked(comment_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment already liked"
            )
        
        # Like comment
        like_data = {
            'comment_id': comment_id,
            'user_id': current_user.id
        }
        result = like_comment(like_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to like comment"
            )
        
        logger.info(f"✅ User {current_user.email} liked comment: {comment_id}")
        
        return {
            "success": True,
            "message": "Comment liked successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error liking comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/{comment_id}/like", response_model=dict)
async def unlike_comment_endpoint(
    post_id: str,
    comment_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Unlike a forum comment
    """
    try:
        logger.info(f"🔍 User {current_user.email} unliking comment: {comment_id}")
        
        # Check if comment exists
        comment_data = get_forum_comment_by_id(comment_id)
        if not comment_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Verify comment belongs to post
        if comment_data['post_id'] != post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment does not belong to this post"
            )
        
        # Check if actually liked
        if not is_comment_liked(comment_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment not liked"
            )
        
        # Unlike comment
        result = unlike_comment(comment_id, current_user.id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to unlike comment"
            )
        
        logger.info(f"✅ User {current_user.email} unliked comment: {comment_id}")
        
        return {
            "success": True,
            "message": "Comment unliked successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error unliking comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/{comment_id}/report", response_model=dict)
async def report_comment_endpoint(
    post_id: str,
    comment_id: str,
    report_data: PostReportCreate,  # Reuse from forum_posts
    current_user: User = Depends(get_current_user)
):
    """
    Report a forum comment
    """
    try:
        logger.info(f"🔍 User {current_user.email} reporting comment: {comment_id}")
        
        # Check if comment exists
        comment_data = get_forum_comment_by_id(comment_id)
        if not comment_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Verify comment belongs to post
        if comment_data['post_id'] != post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment does not belong to this post"
            )
        
        # Create report
        report_dict = report_data.dict()
        report_dict['comment_id'] = comment_id
        report_dict['reporter_id'] = current_user.id
        
        result = create_forum_report(report_dict)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to report comment"
            )
        
        logger.info(f"✅ User {current_user.email} reported comment: {comment_id}")
        
        return {
            "success": True,
            "message": "Comment reported successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error reporting comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )