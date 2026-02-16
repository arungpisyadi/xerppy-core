# Xerppy ERP Framework

Production-grade full-stack Python ERP framework built with Flask and React.

## Overview

Xerppy is a modular, production-ready ERP (Enterprise Resource Planning) framework designed for flexibility and scalability. It provides a solid foundation for building business applications with built-in support for authentication, database management, AI integration, and a powerful plugin system.

## Tech Stack

### Backend
- **Python 3.12+** - Modern Python with type hints
- **Flask 3.1.0** - Lightweight WSGI web application framework
- **Flask-SQLAlchemy 3.1.1** - ORM integration
- **Flask-Migrate 4.0.7** - Database migration management
- **Flask-Login 0.6.3** - User session management

### Frontend
- **React 19** - UI library
- **Vite 6.0** - Build tool
- **Tailwind CSS v4** - Utility-first CSS framework
- **React Router v7** - Client-side routing
- **Axios** - HTTP client

### Database
- **MySQL 8.0** - Default database
- **PostgreSQL** - Supported
- **SQLite** - Development default
- **Supabase** - Cloud PostgreSQL support

### AI Integration
- **CrewAI** - Multi-agent AI framework with tools

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## Features

### Modular Monolith Architecture
- **Application Factory Pattern** - Clean separation of concerns
- **Blueprint-based routing** - Organized endpoint structure
- **Plugin Engine** - Extensible functionality via entry points

### Authentication System
- **Local Authentication** - Email/password with secure password hashing
- **Google SSO** - OAuth 2.0 integration via Authlib
- **LDAP Support** - Enterprise directory integration

### Database Management
- **Multiple Database Support** - MySQL, PostgreSQL, SQLite, Supabase
- **Alembic Migrations** - Version-controlled schema changes
- **SQLAlchemy ORM** - Database abstraction layer

### AI Integration
- **CrewAI Integration** - Multi-agent AI workflows
- **Database Query Tool** - Natural language database access

### Plugin System
- **Entry Point Discovery** - Automatic plugin loading
- **Blueprint Registration** - Plugin routes integration
- **Application Hooks** - Lifecycle event handling

## Project Structure

```
xerppy-core/
├── core/                          # Backend application
│   ├── __init__.py               # Package initialization
│   ├── app.py                    # Flask application factory
│   ├── extensions.py            # Flask extensions setup
│   ├── models.py                # SQLAlchemy models
│   ├── ai/                       # AI integration
│   │   ├── __init__.py
│   │   ├── crew_manager.py      # CrewAI management
│   │   └── database_query_tool.py
│   ├── plugins/                  # Plugin system
│   │   ├── __init__.py
│   │   ├── manager.py            # Plugin manager
│   │   └── sample.py             # Sample plugin
├── docker/                       # Docker configuration
│   ├── Dockerfile                # Container definition
│   └── docker-compose.yml        # Multi-container setup
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── pages/                # Page components
│   │   ├── services/             # API services
│   │   ├── App.tsx              # Main app component
│   │   ├── main.tsx             # Entry point
│   │   └── index.css            # Global styles
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── .env.example                  # Environment template
├── manage.py                     # CLI management script
├── pyproject.toml                # Python project config
└── README.md                     # This file
```

## Quick Start

### Prerequisites

- Python 3.12 or higher
- Node.js 20 or higher
- Docker and Docker Compose (for containerized deployment)
- [uv](https://github.com/astral-sh/uv) - Python package manager

### Installation Steps

1. **Clone and setup dependencies**

   ```bash
   uv sync
   ```

2. **Copy environment configuration**

   ```bash
   cp .env.example .env
   ```

3. **Initialize and run database migrations**

   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

4. **Seed admin user**

   ```bash
   flask seed
   ```

5. **Install frontend dependencies**

   ```bash
   cd frontend
   npm install
   ```

6. **Start development servers**

   Terminal 1 (Frontend):
   ```bash
   cd frontend
   npm run dev
   ```

   Terminal 2 (Backend):
   ```bash
   flask run
   ```

7. **Access the application**

   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8003

## Docker Deployment

### Using Docker Compose

The project includes a production-ready Docker configuration with MySQL, web server, and migration services.

```bash
cd docker
docker-compose up -d
```

### Services

| Service   | Description         | Port  |
|-----------|---------------------|-------|
| web       | Flask application   | 8000  |
| db        | MySQL 8.0 database | 3306  |
| migration | Database migrations | -     |

### Running Migrations in Docker

```bash
cd docker
docker-compose up -d migration
```

## Using Remote Databases

Xerppy supports connecting to remote databases (AWS RDS, Supabase, Azure Database, Google Cloud SQL, etc.) as an alternative to the local MySQL container.

### Quick Setup

1. **Set DB_TYPE to remote** in your `.env` file:

```env
DB_TYPE=remote
REMOTE_DB_URL=your-connection-string-here
```

2. **Start the web service** (no need to start the local db):

```bash
cd docker
docker-compose up -d web
```

### Database Connection Examples

#### AWS RDS (MySQL)

```env
DB_TYPE=remote
REMOTE_DB_URL=mysql+pymysql://username:password@database-endpoint.rds.amazonaws.com:3306/database_name
```

#### AWS RDS (PostgreSQL)

```env
DB_TYPE=remote
REMOTE_DB_URL=postgresql://username:password@database-endpoint.rds.amazonaws.com:5432/database_name
```

#### Supabase

```env
DB_TYPE=supabase
SUPABASE_DB_URL=postgresql://postgres:your-password@db.project-ref.supabase.co:5432/postgres
```

#### Azure Database

```env
DB_TYPE=remote
REMOTE_DB_URL=mysql+pymysql://username:password@server-name.mysql.database.azure.com:3306/database_name
```

#### Google Cloud SQL

```env
DB_TYPE=remote
REMOTE_DB_URL=mysql+pymysql://username:password@/cloudsql/project:region:instance/database
```

### Using Local MySQL Container

If you prefer to use the local MySQL container instead of a remote database:

```bash
cd docker
# Start with local MySQL database
docker-compose --profile local-db up -d
```

The `--profile local-db` flag starts the MySQL container along with the web service.

### Environment Variables Reference

| Variable        | Description                                    | Required for Remote DB |
|-----------------|-----------------------------------------------|------------------------|
| `DB_TYPE`       | Database type: local, remote, supabase, etc. | Yes                    |
| `REMOTE_DB_URL` | Full connection string for remote database   | Yes (when DB_TYPE=remote) |
| `SUPABASE_DB_URL` | Supabase PostgreSQL connection string     | Yes (when DB_TYPE=supabase) |
| `DB_HOST`       | Database host (for local DB_TYPE)            | No                     |
| `DB_PORT`       | Database port (for local DB_TYPE)            | No                     |
| `DB_NAME`       | Database name (for local DB_TYPE)            | No                     |
| `DB_USER`       | Database username (for local DB_TYPE)        | No                     |
| `DB_PASSWORD`   | Database password (for local DB_TYPE)        | No                     |

## CLI Commands

Xerppy provides several CLI commands for managing the application:

| Command                    | Description                           |
|----------------------------|---------------------------------------|
| `flask seed`               | Seed admin user                       |
| `flask setup-supabase`     | Configure Supabase database           |
| `flask create-admin <email> <password>` | Create admin user          |
| `flask list-users`         | List all users in database           |
| `flask db init`            | Initialize migrations                 |
| `flask db migrate`         | Create new migration                 |
| `flask db upgrade`         | Apply migrations                      |
| `flask db downgrade`       | Rollback last migration               |

### Examples

```bash
# Create a new admin user
flask create-admin admin@example.com mypassword123

# List all users
flask list-users

# Configure Supabase
flask setup-supabase
```

## Environment Variables

Configure your application by setting environment variables in the `.env` file:

### Flask Configuration

| Variable      | Description                    | Default                    |
|---------------|--------------------------------|----------------------------|
| `FLASK_ENV`   | Application environment        | `development`              |
| `SECRET_KEY`  | Session secret key             | (auto-generated)           |

### Database Configuration

| Variable        | Description                  | Default         |
|-----------------|------------------------------|-----------------|
| `DB_TYPE`       | Database type                | `sqlite`        |
| `DB_HOST`       | Database host                | `localhost`     |
| `DB_PORT`       | Database port                | `3306`          |
| `DB_NAME`       | Database name                | `xerppy`        |
| `DB_USER`       | Database username            | `root`          |
| `DB_PASSWORD`   | Database password            | -               |
| `SQLITE_PATH`   | SQLite file path             | `xerppy.db`     |

### Supabase Configuration

| Variable          | Description                    |
|-------------------|--------------------------------|
| `SUPABASE_DB_URL` | Supabase PostgreSQL connection |

### LDAP Configuration (Optional)

| Variable        | Description                    |
|-----------------|--------------------------------|
| `LDAP_ENABLED`  | Enable LDAP authentication     |
| `LDAP_HOST`     | LDAP server host              |
| `LDAP_PORT`     | LDAP server port              |
| `LDAP_BASE_DN`  | LDAP base DN                  |
| `LDAP_USE_SSL`  | Use SSL for LDAP              |
| `LDAP_USE_TLS`  | Use TLS for LDAP              |

### Google SSO Configuration (Optional)

| Variable              | Description                    |
|-----------------------|--------------------------------|
| `GOOGLE_CLIENT_ID`    | Google OAuth client ID        |
| `GOOGLE_CLIENT_SECRET`| Google OAuth client secret    |
| `GOOGLE_REDIRECT_URI` | OAuth callback URI           |

### AI Configuration

| Variable        | Description              |
|-----------------|-------------------------|
| `CREWAI_API_KEY`| CrewAI API key         |

### Upload Configuration

| Variable       | Description           | Default   |
|----------------|----------------------|-----------|
| `UPLOAD_FOLDER`| Upload directory     | `uploads` |

## Default Credentials

After running `flask seed`, you can log in with:

- **Email:** admin@xerppy.local
- **Password:** xerppy123

> **Security Note:** Change the default admin password immediately after first login in a production environment.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Follow the existing code style** (use Ruff for linting)
3. **Write tests** for new features and bug fixes
4. **Update documentation** for any changes
5. **Use meaningful commit messages** following conventional commits

### Development Commands

```bash
# Install development dependencies
uv sync --extra dev

# Run linter
ruff check .

# Run type checker
mypy .

# Start development server
flask run
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and feature requests, please open an issue on GitHub.

---

Built with ❤️ using Flask and React
