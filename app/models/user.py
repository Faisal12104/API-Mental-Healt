from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import json

class User:
    def __init__(
        self,
        id: str = None,
        name: str = None,
        email: str = None,
        password: str = None,
        phone: str = None,
        date_of_birth: str = None,
        gender: str = None,
        avatar: str = None,
        preferences: Dict[str, Any] = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.email = email
        self.password = password  # Pastikan password disimpan
        self.phone = phone
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.avatar = avatar
        self.preferences = preferences or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data: dict):
        # Handle preferences from JSON string or dict
        preferences = data.get('preferences', {})
        if isinstance(preferences, str):
            try:
                preferences = json.loads(preferences)
            except:
                preferences = {}
        
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            email=data.get('email'),
            password=data.get('password'),  # Pastikan password diambil
            phone=data.get('phone'),
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender'),
            avatar=data.get('avatar'),
            preferences=preferences,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password': self.password,  # Pastikan password disertakan
            'phone': self.phone,
            'date_of_birth': str(self.date_of_birth) if self.date_of_birth else None,
            'gender': self.gender,
            'avatar': self.avatar,
            'preferences': self.preferences,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }