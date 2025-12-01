from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json

class ForumRoom:
    def __init__(
        self,
        id: str = None,
        name: str = None,
        description: str = None,
        category: str = None,
        icon: str = "💬",
        member_count: int = 0,
        post_count: int = 0,
        last_activity: Optional[datetime] = None,
        is_private: bool = False,
        rules: List[str] = None,
        created_by: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.category = category
        self.icon = icon
        self.member_count = member_count
        self.post_count = post_count
        self.last_activity = last_activity
        self.is_private = is_private
        self.rules = rules or []
        self.created_by = created_by
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data: dict):
        # Handle JSON fields
        rules = data.get('rules', [])
        if isinstance(rules, str):
            try:
                rules = json.loads(rules)
            except:
                rules = []
        
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            category=data.get('category'),
            icon=data.get('icon', '💬'),
            member_count=data.get('member_count', 0),
            post_count=data.get('post_count', 0),
            last_activity=data.get('last_activity'),
            is_private=data.get('is_private', False),
            rules=rules,
            created_by=data.get('created_by'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'icon': self.icon,
            'member_count': self.member_count,
            'post_count': self.post_count,
            'last_activity': self.last_activity.isoformat() if isinstance(self.last_activity, datetime) else self.last_activity,
            'is_private': self.is_private,
            'rules': self.rules,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }

class RoomMember:
    def __init__(
        self,
        id: str = None,
        room_id: str = None,
        user_id: str = None,
        role: str = "member",
        joined_at: datetime = None
    ):
        self.id = id or str(uuid.uuid4())
        self.room_id = room_id
        self.user_id = user_id
        self.role = role
        self.joined_at = joined_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            room_id=data.get('room_id'),
            user_id=data.get('user_id'),
            role=data.get('role', 'member'),
            joined_at=data.get('joined_at')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'user_id': self.user_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if isinstance(self.joined_at, datetime) else self.joined_at
        }