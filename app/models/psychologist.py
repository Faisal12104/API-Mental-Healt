from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json

class Psychologist:
    def __init__(
        self,
        id: str = None,
        name: str = None,
        specialization: List[str] = None,
        experience: int = None,
        rating: float = 0.0,
        price_per_hour: float = None,
        languages: List[str] = None,
        availability: Dict[str, List[str]] = None,
        avatar: Optional[str] = None,
        bio: Optional[str] = None,
        is_available: bool = True,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.specialization = specialization or []
        self.experience = experience or 0
        self.rating = rating
        self.price_per_hour = price_per_hour
        self.languages = languages or []
        self.availability = availability or {}
        self.avatar = avatar
        self.bio = bio
        self.is_available = is_available
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data: dict):
        # Handle JSON fields
        specialization = data.get('specialization', [])
        if isinstance(specialization, str):
            try:
                specialization = json.loads(specialization)
            except:
                specialization = []
        
        languages = data.get('languages', [])
        if isinstance(languages, str):
            try:
                languages = json.loads(languages)
            except:
                languages = []
        
        availability = data.get('availability', {})
        if isinstance(availability, str):
            try:
                availability = json.loads(availability)
            except:
                availability = {}
        
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            specialization=specialization,
            experience=data.get('experience'),
            rating=data.get('rating', 0.0),
            price_per_hour=data.get('price_per_hour'),
            languages=languages,
            availability=availability,
            avatar=data.get('avatar'),
            bio=data.get('bio'),
            is_available=data.get('is_available', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'specialization': self.specialization,
            'experience': self.experience,
            'rating': self.rating,
            'price_per_hour': self.price_per_hour,
            'languages': self.languages,
            'availability': self.availability,
            'avatar': self.avatar,
            'bio': self.bio,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }