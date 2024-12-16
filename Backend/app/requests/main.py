from pydantic import BaseModel, EmailStr, Field

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
