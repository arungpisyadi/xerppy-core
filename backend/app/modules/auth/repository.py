"""Repository layer for auth operations"""
import logging
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

from app.modules.auth.models import User, Role, Permission


class UserRepository:
    """Repository for User model operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        logger.debug(f"[REPO DEBUG] get_by_username called with username: {username}")
        # Eagerly load roles to avoid lazy loading in async context
        stmt = select(User).where(User.username == username).options(selectinload(User.roles))
        logger.debug(f"[REPO DEBUG] SQL query: {stmt}")
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            logger.debug(f"[REPO DEBUG] User found - id: {user.id}, username: {user.username}, email: {user.email}")
            logger.debug(f"[REPO DEBUG] User roles count: {len(user.roles) if user.roles else 0}")
        else:
            logger.warning(f"[REPO DEBUG] User NOT found for username: {username}")
        return user
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        # Eagerly load roles to avoid lazy loading in async context
        stmt = select(User).where(User.email == email).options(selectinload(User.roles))
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            logger.debug(f"[REPO DEBUG] User roles count: {len(user.roles) if user.roles else 0}")
        return user
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_with_roles(self, user_id: int) -> Optional[User]:
        """Get user with roles loaded"""
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, user: User) -> User:
        """Create a new user"""
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def update(self, user: User) -> User:
        """Update an existing user"""
        await self.session.commit()
        await self.session.refresh(user)
        return user


class RoleRepository:
    """Repository for Role model operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name"""
        stmt = select(Role).where(Role.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        stmt = select(Role).where(Role.id == role_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Role]:
        """Get all roles"""
        stmt = select(Role)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_all_with_permissions(self) -> List[Role]:
        """Get all roles with permissions loaded"""
        stmt = select(Role).options(selectinload(Role.permissions))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def create(self, role: Role) -> Role:
        """Create a new role"""
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return role
    
    async def seed_defaults(self) -> None:
        """Seed default roles if they don't exist"""
        default_roles = [
            {"name": "admin", "description": "Administrator with full access"},
            {"name": "user", "description": "Regular user with basic access"},
        ]
        
        for role_data in default_roles:
            existing = await self.get_by_name(role_data["name"])
            if not existing:
                role = Role(**role_data)
                self.session.add(role)
        
        await self.session.commit()


class PermissionRepository:
    """Repository for Permission model operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name"""
        stmt = select(Permission).where(Permission.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Permission]:
        """Get all permissions"""
        stmt = select(Permission)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def create(self, permission: Permission) -> Permission:
        """Create a new permission"""
        self.session.add(permission)
        await self.session.commit()
        await self.session.refresh(permission)
        return permission
    
    async def seed_defaults(self) -> None:
        """Seed default permissions if they don't exist"""
        default_permissions = [
            {"name": "users.read", "description": "Read users"},
            {"name": "users.write", "description": "Create/Update users"},
            {"name": "users.delete", "description": "Delete users"},
            {"name": "roles.read", "description": "Read roles"},
            {"name": "roles.write", "description": "Create/Update roles"},
            {"name": "roles.delete", "description": "Delete roles"},
        ]
        
        for perm_data in default_permissions:
            existing = await self.get_by_name(perm_data["name"])
            if not existing:
                permission = Permission(**perm_data)
                self.session.add(permission)
        
        await self.session.commit()
