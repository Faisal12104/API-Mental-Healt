from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import date, time, datetime
from enum import Enum

class ConsultationType(str, Enum):
    CHAT = "chat"
    VIDEO = "video"
    PHONE = "phone"

class ConsultationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ConsultationBase(BaseModel):
    psychologist_id: str
    type: ConsultationType
    preferred_date: date
    preferred_time: time
    duration: int = 60
    reason: str
    urgency: UrgencyLevel = UrgencyLevel.MEDIUM

    @validator('duration')
    def validate_duration(cls, v):
        if v not in [30, 60, 90, 120]:
            raise ValueError('Duration must be 30, 60, 90, or 120 minutes')
        return v

class ConsultationCreate(ConsultationBase):
    pass

class ConsultationUpdate(BaseModel):
    status: Optional[ConsultationStatus] = None
    notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class ConsultationResponse(ConsultationBase):
    id: str
    user_id: str
    status: ConsultationStatus
    price: Optional[float] = None
    notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ConsultationStatusUpdate(BaseModel):
    status: ConsultationStatus
    notes: Optional[str] = None