"""Authentication service with JWT and password hashing"""
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.modules.auth.models import User, Role
from app.modules.auth.repository import UserRepository, RoleRepository, PermissionRepository
from app.modules.auth.schemas import UserCreate, Token, TokenData

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service for password hashing and JWT"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
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
        """Authenticate a user by username and password"""
        user_repo = UserRepository(session)
        user = await user_repo.get_by_username(username)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
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
        admin_role = await role_repo.get_by_name("admin")
        if admin_role:
            all_perms = await perm_repo.get_all()
            admin_role.permissions.extend(all_perms)
            await session.commit()
    
    @staticmethod
    async def get_user_roles(session: AsyncSession, user: User) -> list[str]:
        """Get list of role names for a user"""
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
