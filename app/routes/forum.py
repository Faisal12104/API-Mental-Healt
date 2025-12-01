from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from app.schemas.forum import ForumRoomCreate, ForumRoomResponse, ForumRoomUpdate, RoomMembershipResponse
from app.utils.database import (
    create_forum_room, get_forum_rooms, get_forum_room_by_id, update_forum_room,
    join_room, leave_room, is_room_member, get_room_members, get_user_joined_rooms
)
from app.models.forum import ForumRoom, RoomMember
from app.models.user import User
from app.auth.jwt_handler import verify_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/forum/rooms", tags=["Forum Rooms"])

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

@router.get("", response_model=dict)
async def get_forum_rooms_endpoint(
    current_user: User = Depends(get_current_user),
    category: Optional[str] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Get list of forum rooms with filtering
    """
    try:
        logger.info(f"🔍 Getting forum rooms - category: {category}")
        
        rooms_data = get_forum_rooms(category, page, limit)
        
        # Check if user has joined each room
        rooms_with_membership = []
        for room_data in rooms_data:
            room = ForumRoomResponse(**ForumRoom.from_dict(room_data).to_dict())
            room.is_joined = is_room_member(room.id, current_user.id) is not None
            rooms_with_membership.append(room)
        
        logger.info(f"✅ Retrieved {len(rooms_with_membership)} forum rooms")
        
        return {
            "success": True,
            "data": {
                "rooms": rooms_with_membership,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(rooms_with_membership)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting forum rooms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/joined", response_model=dict)
async def get_joined_rooms(
    current_user: User = Depends(get_current_user)
):
    """
    Get rooms that the user has joined
    """
    try:
        logger.info(f"🔍 Getting joined rooms for user: {current_user.email}")
        
        rooms_data = get_user_joined_rooms(current_user.id)
        rooms = [ForumRoomResponse(**ForumRoom.from_dict(room).to_dict()) for room in rooms_data]
        
        # Mark all as joined
        for room in rooms:
            room.is_joined = True
        
        logger.info(f"✅ Retrieved {len(rooms)} joined rooms for user: {current_user.email}")
        
        return {
            "success": True,
            "data": rooms
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting joined rooms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{room_id}", response_model=dict)
async def get_forum_room_detail(
    room_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get forum room details
    """
    try:
        logger.info(f"🔍 Getting forum room details: {room_id}")
        
        room_data = get_forum_room_by_id(room_id)
        if not room_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Forum room not found"
            )
        
        room = ForumRoomResponse(**ForumRoom.from_dict(room_data).to_dict())
        room.is_joined = is_room_member(room_id, current_user.id) is not None
        
        return {
            "success": True,
            "data": {
                "room": room
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting forum room: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_forum_room_endpoint(
    room_data: ForumRoomCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new forum room
    """
    try:
        logger.info(f"🔍 Creating forum room: {room_data.name}")
        
        room_dict = room_data.dict()
        room = ForumRoom.from_dict(room_dict)
        room.created_by = current_user.id
        
        room_dict_for_db = room.to_dict()
        
        result = create_forum_room(room_dict_for_db)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create forum room"
            )
        
        # Auto-join the creator as admin
        member_data = {
            'room_id': room.id,
            'user_id': current_user.id,
            'role': 'admin'
        }
        join_room(member_data)
        
        room_response = ForumRoomResponse(**room_dict_for_db)
        room_response.is_joined = True
        
        logger.info(f"✅ Forum room created: {room_data.name}")
        
        return {
            "success": True,
            "data": {
                "room": room_response
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating forum room: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/{room_id}/join", response_model=dict)
async def join_room_endpoint(
    room_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Join a forum room
    """
    try:
        logger.info(f"🔍 User {current_user.email} joining room: {room_id}")
        
        # Check if room exists
        room_data = get_forum_room_by_id(room_id)
        if not room_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Forum room not found"
            )
        
        # Check if already joined
        if is_room_member(room_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already joined this room"
            )
        
        # Join room
        member_data = {
            'room_id': room_id,
            'user_id': current_user.id,
            'role': 'member'
        }
        result = join_room(member_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to join room"
            )
        
        logger.info(f"✅ User {current_user.email} joined room: {room_id}")
        
        return {
            "success": True,
            "message": "Successfully joined the room"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error joining room: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/{room_id}/leave", response_model=dict)
async def leave_room_endpoint(
    room_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Leave a forum room
    """
    try:
        logger.info(f"🔍 User {current_user.email} leaving room: {room_id}")
        
        # Check if room exists
        room_data = get_forum_room_by_id(room_id)
        if not room_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Forum room not found"
            )
        
        # Check if user is the creator (cannot leave if creator)
        if room_data['created_by'] == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room creator cannot leave the room. Transfer ownership first."
            )
        
        # Check if actually joined
        if not is_room_member(room_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not a member of this room"
            )
        
        # Leave room
        result = leave_room(room_id, current_user.id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to leave room"
            )
        
        logger.info(f"✅ User {current_user.email} left room: {room_id}")
        
        return {
            "success": True,
            "message": "Successfully left the room"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error leaving room: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{room_id}/members", response_model=dict)
async def get_room_members_endpoint(
    room_id: str,
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page")
):
    """
    Get members of a forum room
    """
    try:
        logger.info(f"🔍 Getting members for room: {room_id}")
        
        # Check if room exists
        room_data = get_forum_room_by_id(room_id)
        if not room_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Forum room not found"
            )
        
        # Check if user has joined the room
        if not is_room_member(room_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Must be a member to view room members"
            )
        
        members_data = get_room_members(room_id, page, limit)
        members = [RoomMembershipResponse(**RoomMember.from_dict(member).to_dict()) for member in members_data]
        
        logger.info(f"✅ Retrieved {len(members)} members for room: {room_id}")
        
        return {
            "success": True,
            "data": {
                "members": members,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(members)
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting room members: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )