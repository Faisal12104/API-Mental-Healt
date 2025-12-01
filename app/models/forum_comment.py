from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class ForumComment:
    def __init__(
        self,
        id: str = None,
        post_id: str = None,
        author_id: str = None,
        content: str = None,
        is_anonymous: bool = False,
        like_count: int = 0,
        is_edited: bool = False,
        edited_at: Optional[datetime] = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or str(uuid.uuid4())
        self.post_id = post_id
        self.author_id = author_id
        self.content = content
        self.is_anonymous = is_anonymous
        self.like_count = like_count
        self.is_edited = is_edited
        self.edited_at = edited_at
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            post_id=data.get('post_id'),
            author_id=data.get('author_id'),
            content=data.get('content'),
            is_anonymous=data.get('is_anonymous', False),
            like_count=data.get('like_count', 0),
            is_edited=data.get('is_edited', False),
            edited_at=data.get('edited_at'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'author_id': self.author_id,
            'content': self.content,
            'is_anonymous': self.is_anonymous,
            'like_count': self.like_count,
            'is_edited': self.is_edited,
            'edited_at': self.edited_at.isoformat() if isinstance(self.edited_at, datetime) else self.edited_at,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }

class CommentLike:
    def __init__(
        self,
        id: str = None,
        comment_id: str = None,
        user_id: str = None,
        created_at: datetime = None
    ):
        self.id = id or str(uuid.uuid4())
        self.comment_id = comment_id
        self.user_id = user_id
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            comment_id=data.get('comment_id'),
            user_id=data.get('user_id'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'comment_id': self.comment_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }