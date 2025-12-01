from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ForumCategory(str, Enum):
    CINTA = "cinta"
    PEKERJAAN = "pekerjaan"
    KELUARGA = "keluarga"
    KESEHATAN = "kesehatan"
    PENDIDIKAN = "pendidikan"
    HOBI = "hobi"
    LAINNYA = "lainnya"

class RoomRole(str, Enum):
    MEMBER = "member"
    MODERATOR = "moderator"
    ADMIN = "admin"

class ForumRoomBase(BaseModel):
    name: str
    description: str
    category: ForumCategory
    icon: Optional[str] = "💬"
    is_private: bool = False
    rules: Optional[List[str]] = None

    @validator('name')
    def validate_name(cls, v):
        if len(v) < 3:
            raise ValueError('Room name must be at least 3 characters long')
        if len(v) > 255:
            raise ValueError('Room name must be less than 255 characters')
        return v

    @validator('description')
    def validate_description(cls, v):
        if len(v) < 10:
            raise ValueError('Description must be at least 10 characters long')
        return v

class ForumRoomCreate(ForumRoomBase):
    pass

class ForumRoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    is_private: Optional[bool] = None
    rules: Optional[List[str]] = None

class ForumRoomResponse(ForumRoomBase):
    id: str
    member_count: int
    post_count: int
    last_activity: Optional[datetime]
    created_by: str
    created_at: datetime
    updated_at: datetime
    is_joined: bool = False

    class Config:
        orm_mode = True

class RoomMembershipResponse(BaseModel):
    room_id: str
    user_id: str
    role: RoomRole
    joined_at: datetime

    class Config:
        orm_mode = True