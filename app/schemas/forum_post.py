from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PostMood(str, Enum):
    HAPPY = "😊"
    SAD = "😢"
    ANXIOUS = "😰"
    ANGRY = "😠"
    CALM = "😌"
    EXCITED = "🤩"
    NEUTRAL = "😐"

class ForumPostBase(BaseModel):
    content: str
    is_anonymous: bool = False
    mood: Optional[PostMood] = None
    tags: Optional[List[str]] = None
    attachments: Optional[List[str]] = None

    @validator('content')
    def validate_content(cls, v):
        if len(v) < 10:
            raise ValueError('Post content must be at least 10 characters long')
        if len(v) > 5000:
            raise ValueError('Post content must be less than 5000 characters')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return v

class ForumPostCreate(ForumPostBase):
    room_id: str

class ForumPostUpdate(BaseModel):
    content: Optional[str] = None
    mood: Optional[PostMood] = None
    tags: Optional[List[str]] = None
    attachments: Optional[List[str]] = None

class ForumPostResponse(ForumPostBase):
    id: str
    room_id: str
    author_id: str
    author_name: str
    author_avatar: Optional[str]
    like_count: int
    comment_count: int
    share_count: int
    is_edited: bool
    edited_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    is_liked: bool = False

    class Config:
        orm_mode = True

class PostLikeResponse(BaseModel):
    post_id: str
    user_id: str
    created_at: datetime

    class Config:
        orm_mode = True

class ReportReason(str, Enum):
    SPAM = "spam"
    INAPPROPRIATE = "inappropriate"
    HARASSMENT = "harassment"
    OTHER = "other"

class PostReportCreate(BaseModel):
    reason: ReportReason
    description: Optional[str] = None

    @validator('description')
    def validate_description(cls, v):
        if v and len(v) > 500:
            raise ValueError('Description must be less than 500 characters')
        return v