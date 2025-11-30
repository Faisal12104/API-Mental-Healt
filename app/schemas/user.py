from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import date

class UserBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None

    class Config:
        orm_mode = True

    @validator('email')
    def email_valid(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v

class UserCreate(UserBase):
    password: str
    preferences: Optional[Dict[str, Any]] = None
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if len(v) > 50:
            raise ValueError('Password must be less than 50 characters long')
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    avatar: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserResponse(UserBase):
    id: str
    avatar: Optional[str] = None
    preferences: Dict[str, Any]
    created_at: str
    updated_at: str

class UserLogin(BaseModel):
    email: str
    password: str
    
    @validator('email')
    def email_valid(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v