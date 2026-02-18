"""Flask Application Factory for Xerppy ERP Framework.

This module provides the create_app() function which serves as the entry point
for creating and configuring the Flask application. It implements the
Application Factory pattern with support for multiple database types,
plugins, LDAP authentication, and SSO integration.
"""

# pyright: reportAttributeAccessIssue=false, reportCallIssue=false, reportArgumentType=false

from __future__ import annotations

import os
from datetime import datetime, timedelta
from importlib.metadata import entry_points
from typing import TYPE_CHECKING, Any

import jwt
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template_string, request

from core.extensions import db, ldap_manager, login_manager, migrate

if TYPE_CHECKING:
    from flask import Flask

# Load environment variables from .env file
load_dotenv()


class Config:
    """Flask configuration class for Xerppy ERP Framework.

    This class reads configuration values from environment variables and
    builds the database URI dynamically based on the DB_TYPE setting.

    Environment Variables:
        FLASK_ENV: Application environment (development/production)
        SECRET_KEY: Flask secret key for sessions
        DB_TYPE: Database type (mysql/postgres/supabase/sqlite)
        DB_HOST: Database host
        DB_PORT: Database port
        DB_NAME: Database name
        DB_USER: Database username
        DB_PASSWORD: Database password
        SUPABASE_DB_URL: Supabase PostgreSQL connection string
        SQLITE_PATH: Path to SQLite database file
        LDAP_HOST: LDAP server host
        LDAP_PORT: LDAP server port
        LDAP_BASE_DN: LDAP base distinguished name
        LDAP_ENABLED: Enable LDAP authentication
        GOOGLE_CLIENT_ID: Google OAuth client ID
        GOOGLE_CLIENT_SECRET: Google OAuth client secret
        CREWAI_API_KEY: CrewAI API key
    """

    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        # Core configuration
        self.FLASK_ENV = os.getenv("FLASK_ENV", "development")
        self.DEBUG = self.FLASK_ENV == "development"
        self.TESTING = False
        self.SECRET_KEY = os.getenv("SECRET_KEY") or "dev-secret-key-change-in-production"

        # Database configuration
        self.DB_TYPE = os.getenv("DB_TYPE", "sqlite")
        self.SQLALCHEMY_DATABASE_URI = self._build_database_uri()
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SQLALCHEMY_ENGINE_OPTIONS: dict[str, Any] = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
        }

        # LDAP configuration
        self.LDAP_ENABLED = os.getenv("LDAP_ENABLED", "false").lower() == "true"
        self.LDAP_HOST = os.getenv("LDAP_HOST", "ldap://localhost")
        self.LDAP_PORT = int(os.getenv("LDAP_PORT", "389"))
        self.LDAP_BASE_DN = os.getenv("LDAP_BASE_DN", "")
        self.LDAP_USE_SSL = os.getenv("LDAP_USE_SSL", "false").lower() == "true"
        self.LDAP_USE_TLS = os.getenv("LDAP_USE_TLS", "false").lower() == "true"
        self.LDAP_USER_DN = os.getenv(
            "LDAP_USER_DN", "uid={username},ou=users,{base}"
        )

        # Google SSO configuration (Authlib)
        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
        self.GOOGLE_REDIRECT_URI = os.getenv(
            "GOOGLE_REDIRECT_URI", "http://localhost:8003/auth/google/callback"
        )

        # Session configuration
        self.SESSION_COOKIE_SECURE = self.FLASK_ENV == "production"
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SAMESITE = "Lax"
        self.PERMANENT_SESSION_LIFETIME = 3600 * 24 * 7  # 7 days

        # CrewAI configuration
        self.CREWAI_API_KEY = os.getenv("CREWAI_API_KEY")

        # Upload configuration
        self.MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
        self.UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

    def _build_database_uri(self) -> str:
        """Build database URI based on DB_TYPE.

        DB_TYPE Options:
            - local   : Use local MySQL container (same as mysql)
            - remote  : Use remote database - requires REMOTE_DB_URL
            - supabase: Use Supabase PostgreSQL - requires SUPABASE_DB_URL
            - mysql   : Use local MySQL
            - postgres: Use local PostgreSQL
            - sqlite  : Use local SQLite (default)

        Returns:
            SQLAlchemy database URI string.
        """
        db_type = self.DB_TYPE.lower()

        # Handle 'local' as MySQL (for Docker local development)
        if db_type == "local":
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "3306")
            name = os.getenv("DB_NAME", "xerppy")
            user = os.getenv("DB_USER", "root")
            password = os.getenv("DB_PASSWORD", "")
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"

        # Handle remote database (AWS RDS, cloud DBs, etc.)
        if db_type == "remote":
            remote_url = os.getenv("REMOTE_DB_URL")
            if remote_url:
                return remote_url
            # Fallback to local MySQL if REMOTE_DB_URL not provided
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "3306")
            name = os.getenv("DB_NAME", "xerppy")
            user = os.getenv("DB_USER", "root")
            password = os.getenv("DB_PASSWORD", "")
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"

        if db_type == "mysql":
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "3306")
            name = os.getenv("DB_NAME", "xerppy")
            user = os.getenv("DB_USER", "root")
            password = os.getenv("DB_PASSWORD", "")
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"

        if db_type == "postgres":
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "5432")
            name = os.getenv("DB_NAME", "xerppy")
            user = os.getenv("DB_USER", "postgres")
            password = os.getenv("DB_PASSWORD", "")
            return f"postgresql://{user}:{password}@{host}:{port}/{name}"

        if db_type == "supabase":
            # Use Supabase PostgreSQL URI directly (treat as PostgreSQL)
            supabase_url = os.getenv("SUPABASE_DB_URL")
            if supabase_url:
                return supabase_url
            # Fallback to default Supabase connection
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "5432")
            name = os.getenv("DB_NAME", "postgres")
            user = os.getenv("DB_USER", "postgres")
            password = os.getenv("DB_PASSWORD", "")
            return f"postgresql://{user}:{password}@{host}:{port}/{name}"

        # Default to SQLite
        sqlite_path = os.getenv("SQLITE_PATH", "xerppy.db")
        return f"sqlite:///{sqlite_path}"


class DevelopmentConfig(Config):
    """Development-specific configuration."""

    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production-specific configuration."""

    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing-specific configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# Configuration mapping
CONFIG_MAP: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application.

    This is the main entry point for the Xerppy ERP Framework. It creates
    a Flask application instance, loads configuration, initializes extensions,
    registers blueprints, sets up error handlers, and discovers plugins.

    Args:
        config_name: Configuration name (development/production/testing).
                    If None, uses FLASK_ENV environment variable or 'default'.

    Returns:
        Configured Flask application instance.
    """
    # Determine configuration
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")

    # Create Flask application
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    # Load configuration
    config_class = CONFIG_MAP.get(config_name, DevelopmentConfig)
    app.config.from_object(config_class())

    # Initialize extensions
    _init_extensions(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Register CLI commands
    _register_cli_commands(app)

    # Register health check endpoint
    _register_health_check(app)

    # Discover and load plugins
    _load_plugins(app)

    return app


def _init_extensions(app: Flask) -> None:
    """Initialize Flask extensions with the application.

    Args:
        app: The Flask application instance.
    """
    # Initialize SQLAlchemy
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate.init_app(app, db)

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # type: ignore[assignment]
    login_manager.login_message = "Please log in to access this page."
    login_manager.session_protection = "strong"

    # Import User model to register with Flask-Login
    from core.models import User  # noqa: PLC0415

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        """Load user by ID for Flask-Login."""
        return User.query.get(int(user_id))  # type: ignore[no-any-return]

    # Initialize LDAP manager if enabled
    if app.config.get("LDAP_ENABLED"):
        ldap_manager.init_app(app)


def _register_blueprints(app: Flask) -> None:
    """Register Flask blueprints for the application.

    Args:
        app: The Flask application instance.
    """
    # Import blueprints
    from flask import Blueprint

    # Create main blueprint
    main_bp = Blueprint(
        "main",
        __name__,
        template_folder="../templates",
    )

    @main_bp.route("/")
    def index() -> str:
        """Main index page."""
        return render_template_string(
            "<!DOCTYPE html><html><head><title>Xerppy ERP</title></head>"
            "<body><h1>Welcome to Xerppy ERP Framework</h1>"
            "<p>Your production-grade full-stack Python ERP solution.</p>"
            "</body></html>"
        )

    # Create auth blueprint
    auth_bp = Blueprint(
        "auth",
        __name__,
        url_prefix="/auth",
        template_folder="../templates/auth",
    )

    @auth_bp.route("/login")
    def login() -> str:
        """Login page."""
        return render_template_string(
            "<!DOCTYPE html><html><head><title>Login - Xerppy</title></head>"
            "<body><h1>Login</h1><form method='post'>"
            "<input type='email' name='email' placeholder='Email' required><br>"
            "<input type='password' name='password' placeholder='Password' required><br>"
            "<button type='submit'>Login</button></form></body></html>"
        )

    @auth_bp.route("/register")
    def register() -> str:
        """Registration page."""
        return render_template_string(
            "<!DOCTYPE html><html><head><title>Register - Xerppy</title></head>"
            "<body><h1>Register</h1><form method='post'>"
            "<input type='email' name='email' placeholder='Email' required><br>"
            "<input type='password' name='password' placeholder='Password' required><br>"
            "<button type='submit'>Register</button></form></body></html>"
        )

    @auth_bp.route("/logout")
    def logout() -> str:
        """Logout action."""
        from flask_login import logout_user

        logout_user()
        return "Logged out successfully"

    # Create API blueprint for JSON endpoints
    api_bp = Blueprint(
        "api",
        __name__,
        url_prefix="/api",
    )

    @api_bp.route("/auth/login", methods=["POST"])
    def api_login() -> tuple[dict[str, Any], int]:
        """API login endpoint that returns JWT tokens."""
        from core.models import User

        data = request.get_json()
        if not data:
            return {"success": False, "message": "No data provided"}, 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {"success": False, "message": "Email and password are required"}, 400

        # Find user by email
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return {"success": False, "message": "Invalid email or password"}, 401

        # Generate tokens
        secret_key = app.config.get("SECRET_KEY") or "dev-secret-key-change-in-production"

        # Access token (expires in 1 hour)
        access_payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(hours=1),
            "type": "access",
        }
        access_token = jwt.encode(access_payload, secret_key, algorithm="HS256")

        # Refresh token (expires in 7 days)
        refresh_payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(days=7),
            "type": "refresh",
        }
        refresh_token = jwt.encode(refresh_payload, secret_key, algorithm="HS256")

        return {
            "success": True,
            "accessToken": access_token,
            "refreshToken": refresh_token,
        }, 200

    @api_bp.route("/auth/logout", methods=["POST"])
    def api_logout() -> tuple[dict[str, Any], int]:
        """API logout endpoint."""
        return {"success": True, "message": "Logged out successfully"}, 200

    @api_bp.route("/auth/refresh", methods=["POST"])
    def api_refresh() -> tuple[dict[str, Any], int]:
        """Refresh access token endpoint."""
        data = request.get_json()
        if not data or not data.get("refreshToken"):
            return {"success": False, "message": "Refresh token required"}, 400

        try:
            secret_key = app.config.get("SECRET_KEY") or "dev-secret-key-change-in-production"
            payload = jwt.decode(data["refreshToken"], secret_key, algorithms=["HS256"])

            if payload.get("type") != "refresh":
                return {"success": False, "message": "Invalid token type"}, 401

            # Generate new access token
            access_payload = {
                "user_id": payload["user_id"],
                "email": payload["email"],
                "exp": datetime.utcnow() + timedelta(hours=1),
                "type": "access",
            }
            access_token = jwt.encode(access_payload, secret_key, algorithm="HS256")

            return {
                "success": True,
                "accessToken": access_token,
            }, 200
        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "Token expired"}, 401
        except jwt.InvalidTokenError:
            return {"success": False, "message": "Invalid token"}, 401

    # Register blueprints with the app
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)


def _register_error_handlers(app: Flask) -> None:
    """Register error handlers for common HTTP errors.

    Args:
        app: The Flask application instance.
    """

    @app.errorhandler(404)
    def not_found_error(error: Any) -> tuple[str, int]:
        """Handle 404 Not Found errors."""
        return render_template_string(
            "<!DOCTYPE html><html><head><title>404 - Not Found</title></head>"
            "<body><h1>404 - Page Not Found</h1>"
            "<p>The page you are looking for does not exist.</p>"
            "<a href='/'>Go to Home</a></body></html>"
        ), 404

    @app.errorhandler(500)
    def internal_error(error: Any) -> tuple[str, int]:
        """Handle 500 Internal Server errors."""
        # Rollback any failed database transactions
        db.session.rollback()
        return render_template_string(
            "<!DOCTYPE html><html><head><title>500 - Internal Server Error</title></head>"
            "<body><h1>500 - Internal Server Error</h1>"
            "<p>An unexpected error occurred. Please try again later.</p>"
            "<a href='/'>Go to Home</a></body></html>"
        ), 500


def _register_cli_commands(app: Flask) -> None:
    """Register Flask CLI commands.

    Args:
        app: The Flask application instance.
    """
    import click

    @app.cli.command("seed")
    def seed_command() -> None:
        """Seed the database with initial data.

        Creates an admin user if the database is empty.
        """
        from core.models import seed_admin

        click.echo("Seeding database...")
        admin = seed_admin()
        if admin:
            click.echo(f"Admin user created: {admin.email}")
        else:
            click.echo("Admin user already exists or database not empty.")
        click.echo("Database seeding completed.")

    @app.cli.command("setup-supabase")
    def setup_supabase_command() -> None:
        """Setup Supabase configuration.

        This command will be implemented in manage.py for more complex
        Supabase setup operations.
        """
        click.echo("Setting up Supabase...")
        click.echo(
            "Note: This is a placeholder. For full Supabase setup, "
            "use the manage.py script."
        )
        click.echo("Supabase setup command executed.")


def _register_health_check(app: Flask) -> None:
    """Register health check endpoint.

    Args:
        app: The Flask application instance.
    """

    @app.route("/health")
    def health_check() -> tuple[Any, int]:
        """Health check endpoint for monitoring.

        Returns:
            Tuple of JSON response and HTTP status code.
        """
        health_status: dict[str, str] = {
            "status": "healthy",
            "app": "xerppy",
            "version": "0.1.0",
        }

        # Check database connection
        try:
            db.session.execute(db.text("SELECT 1"))
            health_status["database"] = "connected"
        except Exception:
            health_status["database"] = "disconnected"
            health_status["status"] = "degraded"

        return jsonify(health_status), 200


def _load_plugins(app: Flask) -> None:
    """Discover and load plugins with entry point group 'xerppy.plugins'.

    Plugins can register Blueprints and Models with the application.
    This allows for extensible functionality through the plugin system.

    Args:
        app: The Flask application instance.
    """
    try:
        # Get entry points for xerppy.plugins group
        plugins = entry_points(group="xerppy.plugins")

        for plugin in plugins:
            try:
                plugin_entry = plugin.load()
                plugin_name = plugin.name

                # Initialize plugin if it has an init_app function
                if hasattr(plugin_entry, "init_app"):
                    plugin_entry.init_app(app)

                # Register plugin blueprints
                if hasattr(plugin_entry, "register_blueprints"):
                    plugin_entry.register_blueprints(app)

                app.logger.info(f"Loaded plugin: {plugin_name}")

            except Exception as e:
                app.logger.error(f"Failed to load plugin {plugin.name}: {e}")

    except TypeError:
        # Handle older Python/importlib.metadata versions
        try:
            plugins = entry_points().get("xerppy.plugins", [])  # type: ignore[arg-type,misc]
            for plugin in plugins:
                try:
                    plugin_entry = plugin.load()
                    plugin_name = plugin.name

                    if hasattr(plugin_entry, "init_app"):
                        plugin_entry.init_app(app)

                    if hasattr(plugin_entry, "register_blueprints"):
                        plugin_entry.register_blueprints(app)

                    app.logger.info(f"Loaded plugin: {plugin_name}")

                except Exception as e:
                    app.logger.error(f"Failed to load plugin {plugin.name}: {e}")
        except Exception:
            # No plugins found or error loading
            pass


# Application instance for WSGI servers
app = create_app()


if __name__ == "__main__":
    # Run development server
    app.run(host="0.0.0.0", port=8003, debug=True)
