"""
Pydantic schemas - API validation
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class StatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in-progress"
    completed = "completed"


# User Schemas
class UserCreate(BaseModel):
    """For registration"""

    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """For login"""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """What we return (no password!)"""

    id: UUID
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Token Schemas
class Token(BaseModel):
    """JWT token response"""

    access_token: str
    token_type: str = "bearer"


# Task Schemas
class TaskCreate(BaseModel):
    """Creating a task"""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: PriorityEnum = PriorityEnum.medium
    status: StatusEnum = StatusEnum.pending


class TaskUpdate(BaseModel):
    """Updating a task (all optional)"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None


class TaskResponse(BaseModel):
    """What we return"""

    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    priority: PriorityEnum
    status: StatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
