from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MoodType(str, Enum):
    VERY_HAPPY = "veryHappy"
    HAPPY = "happy"
    NEUTRAL = "neutral"
    SAD = "sad"
    VERY_SAD = "verySad"
    ANXIOUS = "anxious"
    STRESSED = "stressed"
    CALM = "calm"
    EXCITED = "excited"
    ANGRY = "angry"

class MoodEntryBase(BaseModel):
    mood: MoodType
    energy_level: Optional[int] = None
    sleep_hours: Optional[float] = None
    activities: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    note: Optional[str] = None
    timestamp: Optional[datetime] = None

    @validator('energy_level')
    def validate_energy_level(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError('Energy level must be between 1 and 10')
        return v

    @validator('sleep_hours')
    def validate_sleep_hours(cls, v):
        if v is not None and (v < 3 or v > 12):
            raise ValueError('Sleep hours must be between 3 and 12')
        return v

class MoodEntryCreate(MoodEntryBase):
    pass

class MoodEntryUpdate(BaseModel):
    mood: Optional[MoodType] = None
    energy_level: Optional[int] = None
    sleep_hours: Optional[float] = None
    activities: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    note: Optional[str] = None
    timestamp: Optional[datetime] = None

class MoodEntryResponse(MoodEntryBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        orm_mode = True

class MoodStatisticsResponse(BaseModel):
    period: str
    total_entries: int
    average_mood: float
    average_energy: float
    average_sleep: float
    mood_distribution: Dict[str, int]
    trends: Dict[str, str]
    insights: List[str]

class MoodAnalysisResponse(BaseModel):
    dominant_mood: str
    average_energy: float
    average_sleep: float
    consistency_score: int
    positive_days: int
    correlation: int
    recommendations: List[Dict[str, Any]]
    patterns: Dict[str, Any]