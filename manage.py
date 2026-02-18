"""CLI Management Script for Xerppy ERP Framework.

This module provides command-line interface commands for managing
the Xerppy application, including database seeding, Supabase setup,
user management, and more.
"""

import sys
from pathlib import Path

import click

from core.app import create_app
from core.extensions import db
from core.models import User, seed_admin

# Create Flask app instance
app = create_app()


@app.cli.command("seed")
def seed_command() -> None:
    """Seed the database with admin user.

    Creates a default admin user with email 'admin@xerppy.local'
    and password 'xerppy123' if no users exist in the database.
    """
    with app.app_context():
        click.echo("Seeding database with admin user...")
        admin = seed_admin()
        if admin:
            click.echo(
                "✓ Admin user created successfully!\n"
                "  Email: admin@xerppy.local\n"
                "  Password: xerppy123\n"
                "  Role: admin"
            )
        else:
            click.echo("✗ Admin user already exists or database is not empty.")
        click.echo("Database seeding completed.")


@app.cli.command("setup-supabase")
def setup_supabase_command() -> None:
    """Interactive command to configure Supabase.

    Prompts for Supabase PostgreSQL connection URI and updates
    the .env file with the database configuration.
    """
    click.echo("=== Supabase Setup ===")
    click.echo("This command will configure Supabase as your database provider.")
    click.echo("")

    # Get the Supabase connection URI from user
    supabase_url = click.prompt(
        "Enter your Supabase Connection String (PostgreSQL URI)",
        type=str,
        default="",
    )

    # Basic validation
    if not supabase_url:
        click.echo("✗ Error: Connection string cannot be empty.")
        sys.exit(1)

    if not supabase_url.startswith(("postgresql://", "postgres://")):
        click.echo("✗ Error: Invalid connection string. Must start with 'postgresql://' or 'postgres://'")
        sys.exit(1)

    # Update .env file
    env_path = Path(".env")
    env_example_path = Path(".env.example")

    if not env_path.exists():
        # Create .env from .env.example if it doesn't exist
        if env_example_path.exists():
            click.echo("Creating .env from .env.example...")
            env_content = env_example_path.read_text(encoding="utf-8")
            env_path.write_text(env_content, encoding="utf-8")
        else:
            # Create empty .env file
            env_path.write_text("", encoding="utf-8")

    # Read existing .env content
    env_content = env_path.read_text(encoding="utf-8")
    env_lines = env_content.splitlines()

    # Update or add DB_TYPE and SUPABASE_DB_URL
    db_type_updated = False
    supabase_url_updated = False
    new_lines: list[str] = []

    for line in env_lines:
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            # Keep comments and empty lines
            new_lines.append(line)
        elif stripped.startswith("DB_TYPE="):
            new_lines.append("DB_TYPE=supabase")
            db_type_updated = True
        elif stripped.startswith("SUPABASE_DB_URL="):
            new_lines.append(f"SUPABASE_DB_URL={supabase_url}")
            supabase_url_updated = True
        else:
            new_lines.append(line)

    # Add missing variables if not found
    if not db_type_updated:
        new_lines.append("DB_TYPE=supabase")
    if not supabase_url_updated:
        new_lines.append(f"SUPABASE_DB_URL={supabase_url}")

    # Write updated content
    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    click.echo("")
    click.echo("✓ Supabase configuration updated successfully!")
    click.echo("  DB_TYPE=supabase")
    click.echo(f"  SUPABASE_DB_URL={supabase_url[:30]}...")
    click.echo("")
    click.echo("Please restart your application for changes to take effect.")


@app.cli.command("create-admin")
@click.argument("email")
@click.argument("password")
def create_admin_command(email: str, password: str) -> None:
    """Create an admin user with the specified email and password.

    Args:
        email: The email address for the admin user.
        password: The password for the admin user.
    """
    with app.app_context():
        # Check if user already exists
        existing_user = db.session.execute(
            db.select(User).where(User.email == email)
        ).scalars().first()

        if existing_user:
            click.echo(f"✗ Error: User with email '{email}' already exists.")
            sys.exit(1)

        # Create admin user
        admin = User(
            email=email,
            role=User.ROLE_ADMIN,
            sso_provider=User.SSO_LOCAL,
        )
        admin.set_password(password)

        # Add and commit to database
        db.session.add(admin)
        db.session.commit()

        click.echo(
            f"✓ Admin user created successfully!\n"
            f"  Email: {email}\n"
            f"  Role: admin\n"
            f"  SSO Provider: local"
        )


@app.cli.command("list-users")
def list_users_command() -> None:
    """List all users in the database."""
    with app.app_context():
        users = db.session.execute(db.select(User)).scalars().all()

        if not users:
            click.echo("No users found in the database.")
            return

        # Print table header
        click.echo("")
        click.echo(
            f"{'ID':<5} {'Email':<30} {'Role':<10} {'SSO Provider':<15} {'Created At':<20}"
        )
        click.echo("-" * 85)

        # Print each user
        for user in users:
            created_at = user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "N/A"
            email = user.email[:29] if len(user.email) > 29 else user.email
            role = user.role or "N/A"
            sso_provider = user.sso_provider or "N/A"

            click.echo(
                f"{user.id:<5} {email:<30} {role:<10} {sso_provider:<15} {created_at:<20}"
            )

        click.echo("")
        click.echo(f"Total users: {len(users)}")


def show_available_commands() -> None:
    """Show available CLI commands when running manage.py directly."""
    click.echo("=== Xerppy ERP Management CLI ===")
    click.echo("")
    click.echo("Available commands:")
    click.echo("  flask seed          - Seed database with admin user")
    click.echo("  flask setup-supabase - Configure Supabase database")
    click.echo("  flask create-admin  - Create a specific admin user")
    click.echo("  flask list-users    - List all users in the database")
    click.echo("")
    click.echo("Usage:")
    click.echo("  flask <command> [arguments]")
    click.echo("")
    click.echo("Examples:")
    click.echo("  flask seed")
    click.echo("  flask setup-supabase")
    click.echo("  flask create-admin admin@example.com mypassword")
    click.echo("  flask list-users")


if __name__ == "__main__":
    # Use Flask's CLI to run commands
    # This allows running: python manage.py flask <command>
    # Or simply: flask <command> (when manage.py is in the project root)
    from flask.cli import main as flask_main

    # Check if we should show help or run a command
    if len(sys.argv) > 1:
        sys.argv[0] = "flask"
        flask_main()
    else:
        show_available_commands()
