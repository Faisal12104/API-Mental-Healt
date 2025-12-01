from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from app.schemas.message import MessageCreate, MessageResponse, MarkMessagesRead
from app.utils.database import (
    create_message, get_messages, mark_messages_as_read, 
    get_unread_message_count, get_consultation_by_id
)
from app.models.message import Message
from app.models.user import User
from app.auth.jwt_handler import verify_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/consultations/{consultation_id}/messages", tags=["Messaging"])

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
async def send_message(
    consultation_id: str,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Send a message in consultation
    """
    try:
        logger.info(f"🔍 Sending message in consultation: {consultation_id}")
        
        # Check if consultation exists and user has access
        consultation = get_consultation_by_id(consultation_id)
        if not consultation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation not found"
            )
        
        if consultation['user_id'] != current_user.id and consultation['psychologist_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this consultation"
            )
        
        # Check if consultation is active
        if consultation['status'] not in ['confirmed', 'completed']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send messages in this consultation status"
            )
        
        # Create message object
        message_dict = message_data.dict()
        message = Message.from_dict(message_dict)
        message.consultation_id = consultation_id
        message.sender_id = current_user.id
        
        message_dict_for_db = message.to_dict()
        
        # Save to database
        result = create_message(message_dict_for_db)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send message"
            )
        
        logger.info(f"✅ Message sent in consultation: {consultation_id}")
        
        return {
            "success": True,
            "data": {
                "message": MessageResponse(**message_dict_for_db)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error sending message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("", response_model=dict)
async def get_messages_endpoint(
    consultation_id: str,
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page")
):
    """
    Get messages in consultation
    """
    try:
        logger.info(f"🔍 Getting messages for consultation: {consultation_id}")
        
        # Check if consultation exists and user has access
        consultation = get_consultation_by_id(consultation_id)
        if not consultation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation not found"
            )
        
        if consultation['user_id'] != current_user.id and consultation['psychologist_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this consultation"
            )
        
        # Get messages
        messages_data = get_messages(consultation_id, page, limit)
        messages = [MessageResponse(**Message.from_dict(msg).to_dict()) for msg in messages_data]
        
        # Mark messages as read for the current user
        if messages:
            mark_messages_as_read(consultation_id, current_user.id)
        
        # Get unread count
        unread_count = get_unread_message_count(consultation_id, current_user.id)
        
        logger.info(f"✅ Retrieved {len(messages)} messages for consultation: {consultation_id}")
        
        return {
            "success": True,
            "data": {
                "messages": messages,
                "unread_count": unread_count,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(messages)
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/read", response_model=dict)
async def mark_messages_read_endpoint(
    consultation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Mark all messages as read in consultation
    """
    try:
        logger.info(f"🔍 Marking messages as read in consultation: {consultation_id}")
        
        # Check if consultation exists and user has access
        consultation = get_consultation_by_id(consultation_id)
        if not consultation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation not found"
            )
        
        if consultation['user_id'] != current_user.id and consultation['psychologist_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this consultation"
            )
        
        # Mark messages as read
        result = mark_messages_as_read(consultation_id, current_user.id)
        
        logger.info(f"✅ Messages marked as read in consultation: {consultation_id}")
        
        return {
            "success": True,
            "message": "All messages marked as read"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error marking messages as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )