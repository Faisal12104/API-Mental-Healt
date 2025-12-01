from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json

class Message:
    def __init__(
        self,
        id: str = None,
        consultation_id: str = None,
        sender_id: str = None,
        content: str = None,
        type: str = "text",
        attachments: List[str] = None,
        is_read: bool = False,
        read_at: Optional[datetime] = None,
        created_at: datetime = None
    ):
        self.id = id or str(uuid.uuid4())
        self.consultation_id = consultation_id
        self.sender_id = sender_id
        self.content = content
        self.type = type
        self.attachments = attachments or []
        self.is_read = is_read
        self.read_at = read_at
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data: dict):
        # Handle JSON fields
        attachments = data.get('attachments', [])
        if isinstance(attachments, str):
            try:
                attachments = json.loads(attachments)
            except:
                attachments = []
        
        return cls(
            id=data.get('id'),
            consultation_id=data.get('consultation_id'),
            sender_id=data.get('sender_id'),
            content=data.get('content'),
            type=data.get('type', 'text'),
            attachments=attachments,
            is_read=data.get('is_read', False),
            read_at=data.get('read_at'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'consultation_id': self.consultation_id,
            'sender_id': self.sender_id,
            'content': self.content,
            'type': self.type,
            'attachments': self.attachments,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if isinstance(self.read_at, datetime) else self.read_at,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }