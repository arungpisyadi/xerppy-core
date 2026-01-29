"""Pydantic schemas for authentication"""
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import List, Optional


# User schemas
class UserCreate(BaseModel):
    """Schema for creating a new user"""
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserWithRoles(BaseModel):
    """Schema for user with roles"""
    id: int
    username: str
    email: str
    is_active: bool
    roles: List[str] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


# Role schemas
class RoleCreate(BaseModel):
    """Schema for creating a role"""
    name: str
    description: Optional[str] = None
    permissions: List[str] = []


class RoleResponse(BaseModel):
    """Schema for role response"""
    id: int
    name: str
    description: Optional[str]
    permissions: List[str] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


# Permission schemas
class PermissionResponse(BaseModel):
    """Schema for permission response"""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Token schemas
class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for JWT token payload"""
    username: Optional[str] = None
    role: Optional[str] = None


# Login schema
class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str
    password: str
