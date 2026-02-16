"""SQLAlchemy models for the Xerppy ERP framework.

This module defines the database models using Flask-SQLAlchemy with
SQLAlchemy 2.0 style and proper type hints.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from flask_login import UserMixin
from sqlalchemy import DateTime, DefaultClause, String, func
from sqlalchemy.orm import Mapped, mapped_column

from core.extensions import db

if TYPE_CHECKING:
    from werkzeug.security import GeneratePasswordHashAlgorithm, CheckPasswordHash


class User(db.Model, UserMixin):
    """User model for authentication and authorization.

    This model represents system users with support for local authentication,
    SSO providers (Google, LDAP), and role-based access control.

    Attributes:
        id: Unique identifier for the user.
        email: User's email address (unique, indexed).
        password_hash: Hashed password for local authentication.
        role: User role (admin, manager, user).
        sso_provider: SSO provider type (local, google, ldap).
        created_at: Timestamp when the user was created.
        updated_at: Timestamp when the user was last updated.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(
        String(50), nullable=False, default="user", server_default="user"
    )
    sso_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Valid roles
    ROLE_ADMIN = "admin"
    ROLE_MANAGER = "manager"
    ROLE_USER = "user"

    # Valid SSO providers
    SSO_LOCAL = "local"
    SSO_GOOGLE = "google"
    SSO_LDAP = "ldap"

    def set_password(self, password: str) -> None:
        """Set the user's password using secure hashing.

        Args:
            password: The plain text password to hash.
        """
        from werkzeug.security import generate_password_hash

        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash.

        Args:
            password: The plain text password to check.

        Returns:
            True if the password matches, False otherwise.
        """
        if self.password_hash is None:
            return False

        from werkzeug.security import check_password_hash

        return check_password_hash(self.password_hash, password)

    def is_admin(self) -> bool:
        """Check if the user has admin role.

        Returns:
            True if user is admin, False otherwise.
        """
        return self.role == self.ROLE_ADMIN

    def is_manager(self) -> bool:
        """Check if the user has manager role.

        Returns:
            True if user is manager, False otherwise.
        """
        return self.role == self.ROLE_MANAGER

    def __repr__(self) -> str:
        """Return string representation of the User instance.

        Returns:
            String representation for debugging.
        """
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"


def seed_admin() -> User | None:
    """Create an admin user if the User table is empty.

    Creates a default admin user with email 'admin@xerppy.local'
    and password 'xerppy123' if no users exist in the database.

    Returns:
        The created User instance, or None if users already exist.
    """
    from core.extensions import db

    # Check if any users exist
    admin_exists = db.session.execute(
        db.select(User)
    ).scalars().first() is not None

    if admin_exists:
        return None

    # Create admin user
    admin = User(
        email="admin@xerppy.local",
        role=User.ROLE_ADMIN,
        sso_provider=User.SSO_LOCAL,
    )
    admin.set_password("xerppy123")

    # Add and commit to database
    db.session.add(admin)
    db.session.commit()

    return admin
