# Alembic Database Migration Setup

This directory contains Alembic migration files for the xerppy project.

## Overview

Alembic is a database migration tool for SQLAlchemy. It helps manage schema changes
over time by generating incremental migration scripts.

## Configuration

The Alembic configuration is located in:
- `alembic.ini` - Main configuration file
- `alembic/env.py` - Environment configuration with async support
- `alembic/script.py.mako` - Template for migration files

## Database Support

This setup supports three database types through `settings.built_database_url`:
- **SQLite** (default) - `sqlite+aiosqlite:///./xerppy.db`
- **PostgreSQL** - `postgresql+asyncpg://user:password@host:port/db`
- **MySQL** - `mysql+aiomysql://user:password@host:port/db`

The database type is configured via the `DATABASE_TYPE` environment variable.

## Quick Start

### 1. Initialize Alembic (already done)

```bash
cd backend
alembic init alembic
```

### 2. Generate a New Migration

After making changes to your models:

```bash
alembic revision -m "description_of_change"
```

This creates a new migration file in `alembic/versions/`.

### 3. Apply Migrations

Apply all pending migrations:

```bash
alembic upgrade head
```

Apply a specific number of migrations:

```bash
alembic upgrade +2
```

### 4. Check Current Migration Status

```bash
alembic current
```

### 5. Show Migration History

```bash
alembic history --verbose
```

### 6. Downgrade Schema

Rollback one migration:

```bash
alembic downgrade -1
```

Rollback to a specific revision:

```bash
alembic downgrade <revision_id>
```

### 7. Generate SQL Script (Offline Mode)

Generate SQL without applying:

```bash
alembic upgrade --sql +1 > migration.sql
```

## Common Commands

| Command | Description |
|---------|-------------|
| `alembic revision -m "message"` | Create new migration |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic downgrade -1` | Rollback last migration |
| `alembic current` | Show current revision |
| `alembic history` | Show migration history |
| `alembic heads` | Show available heads |
| `alembic branches` | Show branching history |
| `alembic stamp head` | Mark current version without running migrations |

## Auto-generate Migrations

To automatically detect model changes:

```bash
alembic revision --autogenerate -m "auto description"
```

**Note:** Review auto-generated migrations carefully before applying.

## Best Practices

1. **Write descriptive migration messages** - Help others understand changes
2. **Test migrations** - Always test upgrade and downgrade paths
3. **Keep migrations idempotent** - Same migration should work regardless of when applied
4. **Use transactions** - Group related changes in single migrations
5. **Review before applying** - Check auto-generated migrations manually

## Directory Structure

```
alembic/
├── alembic.ini          # Configuration
├── env.py              # Environment setup
├── script.py.mako      # Migration template
├── README              # This file
└── versions/           # Migration files
    ├── 20240101_120000_initial_migration.py
    └── ...
```

## Troubleshooting

### Migration fails with "Table already exists"

If tables exist from before migrations were set up:
```bash
alembic stamp head  # Mark current state without applying
```

### Duplicate revision IDs

Ensure all migrations have unique revision IDs. Let Alembic generate them.

### Connection issues

Verify database settings in `.env`:
```env
DATABASE_TYPE=sqlite  # or postgresql or mysql
```

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
