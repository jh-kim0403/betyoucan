from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr

class SignupManual(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str 

class ManualLoginRequest(BaseModel):
    email: EmailStr
    password: str
    timezone: str | None = None

class SignUpResponse(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str

class SignupGoogle(BaseModel):
    id_token: str  # Google ID token from OAuth2

class LoginResponse(BaseModel):

    user_id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    access_token: str
    refresh_token: str

class LogOutRequest(BaseModel):
    refresh_token: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class RefreshRequest(BaseModel):
    user_id: UUID
    refresh_token: str

class RefreshResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    refresh_token: str
    access_token: str