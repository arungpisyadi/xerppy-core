"""Flask extensions initialization for the Xerppy ERP framework.

This module initializes Flask extensions using the Application Factory Pattern.
Extensions are initialized here but not bound to any specific app, allowing
them to be bound later when create_app() is called.

Required Extensions:
- Flask-SQLAlchemy: Database ORM with SQLAlchemy 2.0 style
- Flask-Migrate: Database migrations using Alembic
- Flask-Login: Session management and user authentication
- LDAP3: Enterprise LDAP authentication
"""

# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

from typing import TYPE_CHECKING

import ldap3
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

if TYPE_CHECKING:
    from flask_login import LoginManager as LoginManagerType
    from flask_migrate import Migrate as MigrateType
    from flask_sqlalchemy import SQLAlchemy as SQLAlchemyType
    from ldap3 import Server as ServerType

# Initialize SQLAlchemy with SQLAlchemy 2.0 style
db: SQLAlchemyType = SQLAlchemy()

# Initialize Flask-Migrate
migrate: MigrateType = Migrate()

# Initialize Flask-Login
login_manager: LoginManagerType = LoginManager()


def init_login_manager(app: Flask) -> None:
    """Initialize Flask-Login with the Flask application.

    Args:
        app: The Flask application instance.
    """
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.session_protection = "strong"

    # Import User model here to avoid circular imports
    from core.models import User  # noqa: PLC0415

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        """Load user by ID for Flask-Login.

        Args:
            user_id: The user ID to load.

        Returns:
            User instance if found, None otherwise.
        """
        return User.query.get(int(user_id))  # type: ignore[no-any-return]


# LDAP3 Manager for Enterprise Authentication
class LDAPManager:
    """LDAP3 Manager for enterprise LDAP authentication.

    This class provides LDAP authentication capabilities for enterprise
    environments. It needs to be configured with LDAP server details
    before use.
    """

    def __init__(self) -> None:
        """Initialize the LDAP manager."""
        self._server: ServerType | None = None
        self._base_dn: str | None = None
        self._user_dn: str | None = None
        self._configured: bool = False

    def init_app(self, app: Flask) -> None:
        """Initialize the LDAP manager with Flask app configuration.

        Args:
            app: The Flask application instance.
        """
        ldap_host = app.config.get("LDAP_HOST", "ldap://localhost")
        ldap_port = app.config.get("LDAP_PORT", 389)
        use_ssl = app.config.get("LDAP_USE_SSL", False)
        use_tls = app.config.get("LDAP_USE_TLS", False)
        self._base_dn = app.config.get("LDAP_BASE_DN", "")
        self._user_dn = app.config.get(
            "LDAP_USER_DN", "uid={username},ou=users,{base}"
        )

        server_url = f"{ldap_host}:{ldap_port}"
        self._server = ldap3.Server(
            server_url, get_info=ldap3.ALL, use_ssl=use_ssl
        )

        if use_tls:
            self._server = ldap3.Server(
                server_url,
                get_info=ldap3.ALL,
                use_ssl=use_ssl,
                mode=ldap3.IP_V4_ONLY,
            )

        self._configured = True

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate a user against the LDAP server.

        Args:
            username: The username to authenticate.
            password: The user's password.

        Returns:
            True if authentication successful, False otherwise.
        """
        if (
            not self._configured
            or self._server is None
            or self._base_dn is None
            or self._user_dn is None
        ):
            raise RuntimeError("LDAPManager not configured. Call init_app() first.")

        user_dn = self._user_dn.format(username=username, base=self._base_dn)

        try:
            conn = ldap3.Connection(self._server, user=user_dn, password=password)
            result: bool = conn.bind()
            conn.unbind()
            return result
        except Exception:
            return False

    def search_user(self, username: str) -> dict | None:
        """Search for a user in the LDAP directory.

        Args:
            username: The username to search for.

        Returns:
            Dictionary with user attributes if found, None otherwise.
        """
        if (
            not self._configured
            or self._server is None
            or self._base_dn is None
        ):
            raise RuntimeError("LDAPManager not configured. Call init_app() first.")

        search_filter = f"(uid={username})"

        try:
            conn = ldap3.Connection(self._server, auto_bind=True)
            conn.search(
                search_base=self._base_dn,
                search_filter=search_filter,
                search_scope=ldap3.SUBTREE,
                attributes=["uid", "cn", "sn", "mail", "givenName"],
            )

            if conn.entries:
                entry = conn.entries[0]
                return {
                    "uid": str(entry.uid) if hasattr(entry, "uid") else username,
                    "cn": str(entry.cn) if hasattr(entry, "cn") else "",
                    "sn": str(entry.sn) if hasattr(entry, "sn") else "",
                    "mail": str(entry.mail) if hasattr(entry, "mail") else "",
                    "givenName": str(entry.givenName)
                    if hasattr(entry, "givenName")
                    else "",
                }

            conn.unbind()
            return None
        except Exception:
            return None

    @property
    def is_configured(self) -> bool:
        """Check if LDAP manager is configured.

        Returns:
            True if configured, False otherwise.
        """
        return self._configured


# Create LDAP manager instance
ldap_manager: LDAPManager = LDAPManager()


def init_extensions(app: Flask) -> None:
    """Initialize all Flask extensions with the application.

    This function binds all extensions to the Flask application.

    Args:
        app: The Flask application instance.
    """
    # Initialize SQLAlchemy
    db.init_app(app)

    # Initialize Flask-Migrate with SQLAlchemy
    migrate.init_app(app, db)

    # Initialize Flask-Login
    init_login_manager(app)

    # Initialize LDAP manager if enabled
    if app.config.get("LDAP_ENABLED", False):
        ldap_manager.init_app(app)
