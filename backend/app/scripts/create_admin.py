"""CLI script to create admin user"""
import sys
import asyncio
from getpass import getpass

import typer
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from app.db.connection import AsyncSessionLocal, init_db
from app.modules.auth.models import User, Role
from app.modules.auth.repository import UserRepository, RoleRepository
from app.modules.auth.service import AuthService

app = typer.Typer(help="Create admin user for Xerppy")


async def create_admin_async(
    username: str,
    email: str,
    password: str
):
    """Create admin user asynchronously"""
    # Initialize database
    await init_db()
    
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)
        role_repo = RoleRepository(session)
        
        # Check if user already exists
        existing_user = await user_repo.get_by_username(username)
        if existing_user:
            typer.echo(f"❌ User '{username}' already exists!")
            return False
        
        existing_email = await user_repo.get_by_email(email)
        if existing_email:
            typer.echo(f"❌ Email '{email}' is already registered!")
            return False
        
        # Create admin role if not exists
        admin_role = await role_repo.get_by_name("admin")
        if not admin_role:
            admin_role = Role(
                name="admin",
                description="Administrator with full access"
            )
            admin_role = await role_repo.create(admin_role)
            typer.echo("✅ Created 'admin' role")
        
        # Seed default roles and permissions
        await AuthService.seed_default_roles_and_permissions(session)
        
        # Create admin user
        hashed_password = AuthService.get_password_hash(password)
        admin_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )
        admin_user.roles.append(admin_role)
        
        await user_repo.create(admin_user)
        
        typer.echo(f"✅ Admin user '{username}' created successfully!")
        typer.echo(f"   Email: {email}")
        typer.echo(f"   Role: admin")
        
        return True


@app.command()
def create_admin(
    username: str = typer.Option(..., prompt=True, help="Admin username"),
    email: str = typer.Option(..., prompt=True, help="Admin email"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Admin password"),
):
    """Create an admin user"""
    typer.echo("🔧 Creating admin user...")
    
    try:
        success = asyncio.run(create_admin_async(username, email, password))
        if success:
            typer.echo("\n✨ Admin user setup complete!")
        else:
            typer.echo("\n❌ Admin user creation failed!")
            sys.exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        sys.exit(1)


@app.command()
def interactive():
    """Interactive admin user creation"""
    typer.echo("🔐 Xerppy Admin User Creation")
    typer.echo("=" * 40)
    
    username = typer.prompt("Username")
    email = typer.prompt("Email")
    password = getpass("Password: ")
    confirm_password = getpass("Confirm Password: ")
    
    if password != confirm_password:
        typer.echo("❌ Passwords do not match!")
        sys.exit(1)
    
    if len(password) < 8:
        typer.echo("❌ Password must be at least 8 characters!")
        sys.exit(1)
    
    typer.echo("\n🔧 Creating admin user...")
    
    try:
        success = asyncio.run(create_admin_async(username, email, password))
        if success:
            typer.echo("\n✨ Admin user setup complete!")
        else:
            typer.echo("\n❌ Admin user creation failed!")
            sys.exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()
