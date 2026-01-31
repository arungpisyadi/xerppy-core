"""Authentication service with JWT and password hashing"""
import os
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Workaround for passlib's detect_wrap_bug function which uses a 88-byte test password
# that exceeds bcrypt's 72-byte limit in bcrypt 4.x+
# This MUST be set BEFORE importing passlib
os.environ['PASSLIB_BUG_DETECTOR'] = '0'

import bcrypt

# Workaround for bcrypt 5.x compatibility with passlib
# bcrypt 5.x removed __about__.__version__ which passlib tries to access
# This MUST be applied BEFORE importing passlib
if not hasattr(bcrypt, '__about__'):
    bcrypt.__about__ = type('AboutModule', (), {'__version__': bcrypt.__version__})()

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config.settings import settings
from app.modules.auth.models import User, Role
from app.modules.auth.repository import UserRepository, RoleRepository, PermissionRepository
from app.modules.auth.schemas import UserCreate, Token, TokenData

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Maximum password length for bcrypt
BCRYPT_MAX_PASSWORD_LENGTH = 72


class AuthService:
    """Authentication service for password hashing and JWT"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        logger.debug(f"[SERVICE DEBUG] verify_password called - plain_password_length: {len(plain_password)}, hashed_password_length: {len(hashed_password)}")
        logger.debug(f"[SERVICE DEBUG] hashed_password (first 20 chars): {hashed_password[:20]}...")
        result = pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"[SERVICE DEBUG] verify_password result: {result}")
        return result
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        # Truncate password to 72 bytes (bcrypt maximum)
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > BCRYPT_MAX_PASSWORD_LENGTH:
            password_bytes = password_bytes[:BCRYPT_MAX_PASSWORD_LENGTH]
            password = password_bytes.decode('utf-8', errors='ignore')
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.jwt_access_token_expire_minutes
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt
    
    @staticmethod
    def decode_access_token(token: str) -> Optional[TokenData]:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            username: str = payload.get("sub")
            role: str = payload.get("role")
            if username is None:
                return None
            return TokenData(username=username, role=role)
        except JWTError:
            return None
    
    @staticmethod
    async def authenticate_user(
        session: AsyncSession,
        username: str,
        password: str
    ) -> Optional[User]:
        """Authenticate a user by username or email and password"""
        logger.debug(f"[SERVICE DEBUG] authenticate_user called - username: {username}, password_length: {len(password)}")
        user_repo = UserRepository(session)
        
        # First, try to find user by username
        user = await user_repo.get_by_username(username)
        
        # If not found by username, try to find by email
        if not user:
            logger.debug(f"[SERVICE DEBUG] User not found by username, trying email lookup...")
            user = await user_repo.get_by_email(username)
            if user:
                logger.debug(f"[SERVICE DEBUG] User found by email - id: {user.id}, username: {user.username}, email: {user.email}")
        
        if not user:
            logger.warning(f"[SERVICE DEBUG] User not found for username/email: {username}")
            return None
        
        logger.debug(f"[SERVICE DEBUG] User found - id: {user.id}, username: {user.username}")
        
        # DEBUG: Log password hash details
        logger.debug(f"[SERVICE DEBUG] Stored password hash (first 30 chars): {user.hashed_password[:30]}...")
        
        if not AuthService.verify_password(password, user.hashed_password):
            logger.warning(f"[SERVICE DEBUG] Password verification FAILED for user: {username}")
            return None
        logger.debug(f"[SERVICE DEBUG] Password verification SUCCEEDED for user: {username}")
        return user
    
    @staticmethod
    async def register_user(
        session: AsyncSession,
        user_data: UserCreate,
        role_name: str = "user"
    ) -> User:
        """Register a new user with default role"""
        user_repo = UserRepository(session)
        role_repo = RoleRepository(session)
        
        # Check if user exists
        existing_user = await user_repo.get_by_username(user_data.username)
        if existing_user:
            raise ValueError("Username already registered")
        
        existing_email = await user_repo.get_by_email(user_data.email)
        if existing_email:
            raise ValueError("Email already registered")
        
        # Create user
        hashed_password = AuthService.get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        user = await user_repo.create(user)
        
        # Assign default role
        role = await role_repo.get_by_name(role_name)
        if role:
            user.roles.append(role)
            await user_repo.update(user)
        
        return user
    
    @staticmethod
    async def seed_default_roles_and_permissions(session: AsyncSession) -> None:
        """Seed default roles and permissions"""
        role_repo = RoleRepository(session)
        perm_repo = PermissionRepository(session)
        
        # Seed permissions first
        await perm_repo.seed_defaults()
        
        # Seed roles
        await role_repo.seed_defaults()
        
        # Assign all permissions to admin role
        # Use selectinload to eagerly load permissions relationship
        stmt = select(Role).where(Role.name == "admin").options(selectinload(Role.permissions))
        result = await session.execute(stmt)
        admin_role = result.scalar_one_or_none()
        if admin_role:
            all_perms = await perm_repo.get_all()
            # Filter out permissions that already exist to prevent duplicates
            existing_perm_ids = {perm.id for perm in admin_role.permissions}
            new_perms = [perm for perm in all_perms if perm.id not in existing_perm_ids]
            admin_role.permissions.extend(new_perms)
            await session.commit()
    
    @staticmethod
    async def get_user_roles(session: AsyncSession, user: User) -> list[str]:
        """Get list of role names for a user"""
        logger.debug(f"[SERVICE DEBUG] get_user_roles called for user id: {user.id}")
        logger.debug(f"[SERVICE DEBUG] User roles: {user.roles}")
        logger.debug(f"[SERVICE DEBUG] Roles count: {len(user.roles) if user.roles else 0}")
        return [role.name for role in user.roles]
    
    @staticmethod
    async def has_permission(user: User, permission: str) -> bool:
        """Check if user has a specific permission"""
        for role in user.roles:
            for perm in role.permissions:
                if perm.name == permission:
                    return True
        return False
    
    @staticmethod
    async def has_role(user: User, role_name: str) -> bool:
        """Check if user has a specific role"""
        return any(role.name == role_name for role in user.roles)
