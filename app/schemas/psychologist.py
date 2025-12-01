from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import time
from enum import Enum

class PsychologistBase(BaseModel):
    name: str
    specialization: List[str]
    experience: int
    rating: Optional[float] = 0.0
    price_per_hour: float
    languages: List[str]
    availability: Dict[str, List[str]]
    avatar: Optional[str] = None
    bio: Optional[str] = None
    is_available: Optional[bool] = True

    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 0 or v > 5):
            raise ValueError('Rating must be between 0 and 5')
        return v

    @validator('experience')
    def validate_experience(cls, v):
        if v < 0:
            raise ValueError('Experience cannot be negative')
        return v

class PsychologistResponse(PsychologistBase):
    id: str
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True

class PsychologistCreate(PsychologistBase):
    pass

class PsychologistUpdate(BaseModel):
    name: Optional[str] = None
    specialization: Optional[List[str]] = None
    experience: Optional[int] = None
    rating: Optional[float] = None
    price_per_hour: Optional[float] = None
    languages: Optional[List[str]] = None
    availability: Optional[Dict[str, List[str]]] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    is_available: Optional[bool] = None