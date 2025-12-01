from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class ForumCommentBase(BaseModel):
    content: str
    is_anonymous: bool = False

    @validator('content')
    def validate_content(cls, v):
        if len(v) < 1:
            raise ValueError('Comment content cannot be empty')
        if len(v) > 1000:
            raise ValueError('Comment content must be less than 1000 characters')
        return v

class ForumCommentCreate(ForumCommentBase):
    pass

class ForumCommentUpdate(BaseModel):
    content: Optional[str] = None
    is_anonymous: Optional[bool] = None

class ForumCommentResponse(ForumCommentBase):
    id: str
    post_id: str
    author_id: str
    author_name: str
    author_avatar: Optional[str]
    like_count: int
    is_edited: bool
    edited_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    is_liked: bool = False

    class Config:
        orm_mode = True

class CommentLikeResponse(BaseModel):
    comment_id: str
    user_id: str
    created_at: datetime

    class Config:
        orm_mode = True