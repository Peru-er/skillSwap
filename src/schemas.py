from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, root_validator
from enum import Enum


# Enums
class SkillLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class SkillCategory(str, Enum):
    programming = "programming"
    music = "music"
    sports = "sports"
    languages = "languages"
    art = "art"
    science = "science"
    cooking = "cooking"
    other = "other"


class ExchangeStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    completed = "completed"
    cancelled = "cancelled"


# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    avatar_url: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Skill schemas
class SkillBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    category: SkillCategory
    level: SkillLevel


class SkillCreate(SkillBase):
    can_teach: bool
    want_learn: bool

    @root_validator
    def check_teach_and_learn(cls, values):
        can_teach = values.get('can_teach')
        want_learn = values.get('want_learn')
        if can_teach and want_learn:
            raise ValueError("Не можна одночасно вміти і хотіти вчитися одній навичці")
        return values


class SkillUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    category: Optional[SkillCategory] = None
    level: Optional[SkillLevel] = None
    can_teach: Optional[bool] = None
    want_learn: Optional[bool] = None


class SkillResponse(SkillBase):
    id: int
    can_teach: bool
    want_learn: bool
    created_at: datetime
    updated_at: Optional[datetime]
    users: List['UserResponse'] = Field(default_factory=list)

    class Config:
        from_attributes = True


# Exchange schemas
class ExchangeBase(BaseModel):
    skill_id: int
    message: Optional[str] = Field(None, max_length=500)
    hours_proposed: int = Field(1, ge=1, le=10)


class ExchangeCreate(ExchangeBase):
    receiver_id: int


class ExchangeUpdate(BaseModel):
    status: Optional[ExchangeStatus] = None
    message: Optional[str] = None


class ExchangeResponse(ExchangeBase):
    id: int
    sender_id: int
    receiver_id: int
    status: ExchangeStatus
    created_at: datetime
    updated_at: Optional[datetime]
    sender: 'UserResponse'
    receiver: 'UserResponse'
    skill: 'SkillResponse'

    class Config:
        from_attributes = True


# Review schemas
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)


class ReviewCreate(ReviewBase):
    exchange_id: int


class ReviewResponse(ReviewBase):
    id: int
    exchange_id: int
    reviewer_id: int
    reviewed_id: int
    created_at: datetime
    reviewer: 'UserResponse'
    reviewed: 'UserResponse'

    class Config:
        from_attributes = True


# Update forward references
UserResponse.model_rebuild()
SkillResponse.model_rebuild()
ExchangeResponse.model_rebuild()
ReviewResponse.model_rebuild()

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None
