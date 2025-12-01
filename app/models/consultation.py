from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
import uuid

class Consultation:
    def __init__(
        self,
        id: str = None,
        user_id: str = None,
        psychologist_id: str = None,
        type: str = None,
        status: str = "pending",
        preferred_date: date = None,
        preferred_time: time = None,
        duration: int = 60,
        reason: str = None,
        urgency: str = "medium",
        price: Optional[float] = None,
        notes: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.psychologist_id = psychologist_id
        self.type = type
        self.status = status
        self.preferred_date = preferred_date
        self.preferred_time = preferred_time
        self.duration = duration
        self.reason = reason
        self.urgency = urgency
        self.price = price
        self.notes = notes
        self.scheduled_at = scheduled_at
        self.started_at = started_at
        self.completed_at = completed_at
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            psychologist_id=data.get('psychologist_id'),
            type=data.get('type'),
            status=data.get('status', 'pending'),
            preferred_date=data.get('preferred_date'),
            preferred_time=data.get('preferred_time'),
            duration=data.get('duration', 60),
            reason=data.get('reason'),
            urgency=data.get('urgency', 'medium'),
            price=data.get('price'),
            notes=data.get('notes'),
            scheduled_at=data.get('scheduled_at'),
            started_at=data.get('started_at'),
            completed_at=data.get('completed_at'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'psychologist_id': self.psychologist_id,
            'type': self.type,
            'status': self.status,
            'preferred_date': str(self.preferred_date) if self.preferred_date else None,
            'preferred_time': str(self.preferred_time) if self.preferred_time else None,
            'duration': self.duration,
            'reason': self.reason,
            'urgency': self.urgency,
            'price': self.price,
            'notes': self.notes,
            'scheduled_at': self.scheduled_at.isoformat() if isinstance(self.scheduled_at, datetime) else self.scheduled_at,
            'started_at': self.started_at.isoformat() if isinstance(self.started_at, datetime) else self.started_at,
            'completed_at': self.completed_at.isoformat() if isinstance(self.completed_at, datetime) else self.completed_at,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }