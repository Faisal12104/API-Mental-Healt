from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json

class MoodEntry:
    def __init__(
        self,
        id: str = None,
        user_id: str = None,
        mood: str = None,
        energy_level: Optional[int] = None,
        sleep_hours: Optional[float] = None,
        activities: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        note: Optional[str] = None,
        timestamp: datetime = None,
        created_at: datetime = None
    ):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.mood = mood
        self.energy_level = energy_level
        self.sleep_hours = sleep_hours
        self.activities = activities or []
        self.tags = tags or []
        self.note = note
        self.timestamp = timestamp or datetime.now()
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data: dict):
        # Handle JSON fields
        activities = data.get('activities', [])
        if isinstance(activities, str):
            try:
                activities = json.loads(activities)
            except:
                activities = []
        
        tags = data.get('tags', [])
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except:
                tags = []
        
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            mood=data.get('mood'),
            energy_level=data.get('energy_level'),
            sleep_hours=data.get('sleep_hours'),
            activities=activities,
            tags=tags,
            note=data.get('note'),
            timestamp=data.get('timestamp'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'mood': self.mood,
            'energy_level': self.energy_level,
            'sleep_hours': self.sleep_hours,
            'activities': self.activities,
            'tags': self.tags,
            'note': self.note,
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }