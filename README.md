# Xerppy - Laravel-like FastAPI Starter Kit

<div align="center">

![Xerppy](https://img.shields.io/badge/Xerppy-FastAPI%20Starter%20Kit-blue)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/React-18-cyan)
![License](https://img.shields.io/badge/License-MIT-green)

A Laravel-like FastAPI starter kit with modular monolith architecture, featuring CrewAI integration for AI-powered workflows.

[Features](#features) • [Quickstart](#quickstart-guide) • [Admin Guide](#admin-guide) • [API Documentation](#api-endpoints) • [Production](#production-guide)

</div>

---

## Project Overview

Xerppy is a production-ready FastAPI starter kit inspired by Laravel's architecture patterns. It provides a solid foundation for building modular, scalable web applications with AI capabilities powered by CrewAI.

### What is Xerppy?

Xerppy is designed to bridge the gap between Python's powerful ecosystem and Laravel-inspired application structure. It offers:

- **Modular Monolith Architecture**: Clean separation of concerns with MVC pattern
- **AI Integration**: Built-in CrewAI support for intelligent automation
- **Full-Stack Ready**: React frontend + FastAPI backend in one repository
- **Production-Optimized**: Docker deployment with multi-stage builds

### Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI 0.109+, Python 3.11+ |
| Database | SQLAlchemy 2.0 (Async) with SQLite/Alembic |
| Auth | JWT with password hashing (Passlib) |
| AI | CrewAI 0.30+ with agent workflows |
| Frontend | React 18 with TypeScript + Vite |
| Styling | Tailwind CSS 3.4 |
| Deployment | Docker with multi-stage builds |

### Architecture Description

Xerppy follows a **Modular Monolith** architecture:

```
┌─────────────────────────────────────────────────────┐
│                  Xerppy Application                  │
├─────────────┬─────────────┬─────────────────────────┤
│   Modules   │   Services  │     Controllers         │
│  (Features) │  (Business) │    (Presentation)       │
├─────────────┴─────────────┴─────────────────────────┤
│              Shared Core (Models, Utils)             │
├─────────────────────────────────────────────────────┤
│              Database Layer (SQLAlchemy)             │
└─────────────────────────────────────────────────────┘
```

---

## Features

- ✅ **Modular Architecture** - MVC pattern with clear separation of concerns
- ✅ **Authentication System** - JWT-based auth with role-based permissions
- ✅ **AI Workflows** - CrewAI integration for intelligent automation
- ✅ **Database Migrations** - Alembic for version-controlled schema changes
- ✅ **Production-Ready** - Docker multi-stage builds for minimal images
- ✅ **Type Safety** - Full TypeScript/Python type coverage
- ✅ **Dev Experience** - Hot reload for both frontend and backend

---

## Quickstart Guide

### Prerequisites

- Python 3.11+
- Node.js 20+
- uv (Python package manager)
- npm or pnpm

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies with uv
uv sync

# Create admin user
uv run python -m app.scripts.create_admin interactive

# Start development server
uv run python main.py
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access URLs

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8003 |
| Frontend | http://localhost:5173 |
| API Docs (Swagger) | http://localhost:8003/docs |
| API ReDocs | http://localhost:8003/redoc |

---

## Localhost Development

This project includes setup scripts to help you get started quickly. The scripts check for required dependencies (Python, Node.js, uv) and set up both backend and frontend.

### Prerequisites

**For Linux/macOS/WS2:**
- Bash shell (Linux, macOS, WSL, or Git Bash on Windows)

**For Windows (Native):**
- PowerShell 7+ (download from https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows)
- Run in PowerShell 7+ terminal: `pwsh.exe`

### Quick Start

**Linux/macOS/WS2/Git Bash:**
```bash
./setup.sh setup
```

**Windows (PowerShell 7+):**
```powershell
pwsh.exe .\setup.ps1 setup
```

### Available Commands

**Bash (Linux/macOS/WS2/Git Bash):**
| Command | Description |
|---------|-------------|
| `./setup.sh setup` | Set up entire project (backend + frontend) |
| `./setup.sh setup-backend` | Set up backend only |
| `./setup.sh setup-frontend` | Set up frontend only |
| `./setup.sh start-backend` | Start backend server |
| `./setup.sh start-frontend` | Start frontend server |
| `./setup.sh start-all` | Start both servers |
| `./setup.sh help` | Show help message |

**PowerShell (Windows):**
| Command | Description |
|---------|-------------|
| `.\setup.ps1 setup` | Set up entire project (backend + frontend) |
| `.\setup.ps1 setup-backend` | Set up backend only |
| `.\setup.ps1 setup-frontend` | Set up frontend only |
| `.\setup.ps1 start-backend` | Start backend server |
| `.\setup.ps1 start-frontend` | Start frontend server |
| `.\setup.ps1 start-all` | Start both servers |
| `.\setup.ps1 help` | Show help message |

### What the Setup Does

**Backend:**
1. Checks Python version (reads from backend/.python-version)
2. Installs Python if not present
3. Installs uv package manager
4. Installs Python dependencies with `uv sync`
5. Creates admin user interactively
6. Starts backend server on port 8003

**Frontend:**
1. Checks Node.js installation
2. Installs npm dependencies
3. Starts frontend development server

### Manual Setup (Alternative)

If you prefer to set up manually:

**Backend:**
```bash
cd backend
uv sync
uv run python -m app.scripts.create_admin interactive
uv run python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Admin Guide

### Creating an Admin User

Xerppy includes an interactive CLI script for admin user creation.

#### Interactive Mode (Recommended)

```bash
cd backend
uv run python -m app.scripts.create_admin interactive
```

This will prompt you for:
- Username
- Email
- Password (with confirmation)

#### Non-Interactive Mode

```bash
cd backend
uv run python -m app.scripts.create_admin --username admin --email admin@example.com --password yourpassword
```

### Default Roles

Xerppy seeds the following roles on first run:

| Role | Description |
|------|-------------|
| `admin` | Full system access |
| `user` | Standard authenticated user |
| `viewer` | Read-only access |

### Default Permissions

The system includes CRUD permissions for core entities:

| Permission | Description |
|------------|-------------|
| `create` | Create new resources |
| `read` | View resources |
| `update` | Modify existing resources |
| `delete` | Remove resources |

### Role-Based Access Control (RBAC)

Permissions are assigned to roles automatically. Admin role gets all permissions, while User role gets basic read access.

---

## Project Structure

```
xerppy-core/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # Application entry point
│   │   ├── config/            # Configuration management
│   │   │   ├── __init__.py
│   │   │   └── settings.py    # Pydantic settings
│   │   ├── db/                # Database layer
│   │   │   ├── __init__.py
│   │   │   └── connection.py  # Async SQLAlchemy connection
│   │   ├── modules/           # Feature modules (MVC)
│   │   │   ├── __init__.py
│   │   │   ├── auth/          # Authentication module
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py  # SQLAlchemy models
│   │   │   │   ├── schemas.py # Pydantic schemas
│   │   │   │   ├── router.py  # FastAPI routes
│   │   │   │   ├── service.py # Business logic
│   │   │   │   └── repository.py # Data access
│   │   │   └── ai/            # AI/CrewAI module
│   │   │       ├── __init__.py
│   │   │       ├── config/    # Agent/task configurations
│   │   │       ├── router.py
│   │   │       ├── factory.py
│   │   │       └── flows/     # CrewAI flows
│   │   ├── scripts/           # CLI scripts
│   │   │   ├── __init__.py
│   │   │   └── create_admin.py
│   │   ├── tests/             # Module tests
│   │   │   └── __init__.py
│   │   └── utils/             # Shared utilities
│   │       └── __init__.py
│   ├── tests/                 # Integration tests
│   ├── main.py
│   ├── pyproject.toml
│   └── requirements.txt
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── App.tsx           # Root component
│   │   ├── main.tsx          # Entry point
│   │   ├── context/          # React contexts
│   │   │   └── AuthContext.tsx
│   │   ├── pages/            # Page components
│   │   │   ├── LoginPage.tsx
│   │   │   └── Dashboard.tsx
│   │   ├── services/         # API services
│   │   │   └── authService.ts
│   │   └── index.css         # Global styles
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── Dockerfile                # Multi-stage Docker build
├── docker-compose.yml        # Docker Compose configuration
└── README.md
```

### Backend Structure Explanation

| Directory | Purpose |
|-----------|---------|
| `config/` | Application settings using Pydantic Settings |
| `db/` | Database connection and session management |
| `modules/` | Feature modules following MVC pattern |
| `scripts/` | CLI scripts for admin tasks |
| `tests/` | Unit tests for backend modules |
| `utils/` | Helper functions and utilities |

### Frontend Structure Explanation

| Directory | Purpose |
|-----------|---------|
| `src/context/` | React context providers (Auth, Theme) |
| `src/pages/` | Route page components |
| `src/services/` | API client services |
| `src/components/` | Reusable UI components |

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get JWT token |
| GET | `/api/v1/auth/me` | Get current user info |
| GET | `/api/v1/auth/roles` | List available roles |

### AI Module

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ai/flows/example` | Run example AI flow |
| POST | `/api/v1/ai/knowledge/query` | Query knowledge base |

### Health Checks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API root with status |
| GET | `/health` | Simple health check |

---

## CrewAI Integration

Xerppy includes CrewAI integration for building intelligent AI workflows.

### Configuring Agents

Agents are configured in `backend/app/modules/ai/config/agents.yaml`:

```yaml
agents:
  - name: "ResearchAgent"
    role: "researcher"
    goal: "Gather information about {topic}"
    backstory: "You are an expert researcher..."
```

### Configuring Tasks

Tasks are defined in `backend/app/modules/ai/config/tasks.yaml`:

```yaml
tasks:
  - name: "research_task"
    description: "Research the given topic"
    agent: "ResearchAgent"
    expected_output: "Detailed research report"
```

### Running Flows via API

```bash
# Run example flow
curl -X POST http://localhost:8003/api/v1/ai/flows/example \
  -H "Content-Type: application/json" \
  -d '{"topic": "machine learning"}'
```

---

## Production Guide

### Building with Docker

```bash
# Build the Docker image
docker build -t xerppy .

# Run with Docker Compose (recommended)
docker-compose up -d

# Or run directly
docker run -p 8003:8003 \
  -e DATABASE_URL="sqlite+aiosqlite:///./prod.db" \
  -e SECRET_KEY="your-production-secret-key" \
  xerppy
```

### Environment Variables

All configuration is managed through environment variables. Create a `.env` file in the `backend/` directory based on `.env.example`.

#### Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_NAME` | No | `Xerppy API` | Application name |
| `APP_VERSION` | No | `0.1.0` | Application version |
| `DEBUG` | No | `false` | Enable debug mode |
| `DATABASE_URL` | Yes | `sqlite+aiosqlite:///./xerppy.db` | Database connection string |
| `JWT_SECRET_KEY` | Yes | - | JWT signing secret (use strong key in production) |
| `JWT_ALGORITHM` | No | `HS256` | JWT algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Token expiration time |
| `CORS_ORIGINS` | No | `http://localhost:5173` | Comma-separated CORS origins |
| `BACKEND_HOST` | No | `0.0.0.0` | Backend server host |
| `BACKEND_PORT` | No | `8003` | Backend server port |

#### Frontend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | No | `http://localhost:8003` | Backend API URL |
| `VITE_PORT` | No | `5173` | Frontend dev server port |

#### Example `.env` File

```bash
# Application
APP_NAME="Xerppy API"
APP_VERSION="0.1.0"
DEBUG=false

# Database
DATABASE_URL="sqlite+aiosqlite:///./xerppy.db"

# JWT Authentication
JWT_SECRET_KEY="your-super-secret-key-change-in-production"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS="http://localhost:5173"

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8003
```

### Production Considerations

#### Database

For production, use PostgreSQL instead of SQLite:

```bash
# Example PostgreSQL connection
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/xerppy"
```

#### Secrets Management

- Use environment variables for all secrets
- Consider using Docker secrets or external vault
- Never commit `.env` files to version control

#### Security Checklist

- [ ] Set strong `SECRET_KEY` (minimum 32 characters)
- [ ] Use HTTPS in production
- [ ] Configure proper CORS origins
- [ ] Enable rate limiting (not included by default)
- [ ] Set up proper logging and monitoring

---

## Development Commands

### Running Tests

```bash
# Backend tests
cd backend
uv run pytest

# Backend tests with coverage
uv run pytest --cov=app

# Frontend tests
cd frontend
npm run test
```

### Database Migrations

```bash
# Create new migration
cd backend
uv run alembic revision -m "description"

# Apply migrations
uv run alembic upgrade head

# Check current revision
uv run alembic current
```

### Linting and Formatting

```bash
# Backend (ruff)
cd backend
uv run ruff check .
uv run ruff format .

# Frontend (eslint)
cd frontend
npm run lint
npm run lint:fix
```

### Database Seeding

```bash
# Reset database and seed roles
uv run python -m app.scripts.create_admin --force
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [CrewAI](https://www.crewai.com/) - AI agent framework
- [Laravel](https://laravel.com/) - Architecture inspiration
- [Vite](https://vitejs.dev/) - Frontend build tool

---

<div align="center">
Made with ❤️ by the Xerppy Team
</div>
