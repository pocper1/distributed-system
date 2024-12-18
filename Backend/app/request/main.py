from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# User registration request


class RegisterUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

# User login request


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

# Create team request


class CreateTeamRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., max_length=500)

# User check-in request


class UserCheckinRequest(BaseModel):
    user_id: int
    team_id: int
    content: str

# Update score request


class UpdateScoreRequest(BaseModel):
    team_id: int
    value: float


class CreateEventRequest(BaseModel):
    name: str
    description: str
    start_time: datetime
    end_time: datetime


class JoinTeamRequest(BaseModel):
    user_id: int
    team_id: int


class UploadRequest(BaseModel):
    user_id: int = Field(...,
                         description="The ID of the user uploading the check-in data")
    created_at: datetime = Field(..., description="The timestamp of the upload")
    comment: Optional[str] = Field(
        None, max_length=500, description="Optional comment, max length 500 characters")
    photo: Optional[str] = Field(
        None,
        description="Base64 encoded image string, optional for photo uploads"
    )
