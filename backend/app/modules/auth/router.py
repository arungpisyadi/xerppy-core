"""Authentication API router"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_db
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository, RoleRepository
from app.modules.auth.schemas import (
    UserCreate,
    UserResponse,
    UserWithRoles,
    Token,
    LoginRequest,
    RoleResponse,
)
from app.modules.auth.service import AuthService

# Router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db)
) -> UserWithRoles:
    """Dependency to get current authenticated user"""
    token_data = AuthService.decode_access_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_repo = UserRepository(session)
    user = await user_repo.get_by_username(token_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserWithRoles(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        roles=[role.name for role in user.roles],
        created_at=user.created_at,
    )


async def get_current_active_user(
    current_user: UserWithRoles = Depends(get_current_user)
) -> UserWithRoles:
    """Dependency to get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_admin_user(
    current_user: UserWithRoles = Depends(get_current_active_user)
) -> UserWithRoles:
    """Dependency to require admin role"""
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_db)):
    """Register a new user"""
    try:
        user = await AuthService.register_user(session, user_data)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@auth_router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    session: AsyncSession = Depends(get_db)
):
    """Login and get access token"""
    user = await AuthService.authenticate_user(
        session,
        login_data.username,
        login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    
    # Get user roles
    roles = await AuthService.get_user_roles(session, user)
    primary_role = roles[0] if roles else "user"
    
    access_token = AuthService.create_access_token(
        data={"sub": user.username, "role": primary_role}
    )
    
    return Token(access_token=access_token, token_type="bearer")


@auth_router.get("/me", response_model=UserWithRoles)
async def get_current_user_info(current_user: UserWithRoles = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user


@auth_router.get("/roles", response_model=list[RoleResponse])
async def get_all_roles(
    _: UserWithRoles = Depends(get_admin_user),
    session: AsyncSession = Depends(get_db)
):
    """Get all roles (admin only)"""
    role_repo = RoleRepository(session)
    roles = await role_repo.get_all_with_permissions()
    
    return [
        RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=[perm.name for perm in role.permissions],
            created_at=role.created_at,
        )
        for role in roles
    ]
