from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"

class MessageBase(BaseModel):
    content: str
    type: MessageType = MessageType.TEXT
    attachments: Optional[List[str]] = None

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        return v

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: str
    consultation_id: str
    sender_id: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True

class MarkMessagesRead(BaseModel):
    message_ids: List[str]