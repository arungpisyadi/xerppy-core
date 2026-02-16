# =============================================================================
# Xerppy ERP Framework - Multi-stage Docker Build
# =============================================================================
# Stage 1: Node.js build for React frontend with Vite
# Stage 2: Python production environment with Gunicorn

# -----------------------------------------------------------------------------
# Stage 1: Node Build
# -----------------------------------------------------------------------------
FROM node:20-alpine AS node-build

# Set working directory for frontend
WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install frontend dependencies
RUN npm ci --only=production=false

# Copy frontend source code
COPY frontend/ ./

# Build the React app with Vite
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 2: Python Production
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS python-production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy Python project files
COPY pyproject.toml ./

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY core/ ./core/
COPY manage.py ./
COPY migrations/ ./migrations/ 2>/dev/null || true

# Copy static and templates directories if they exist
COPY static/ ./static/ 2>/dev/null || true
COPY templates/ ./templates/ 2>/dev/null || true

# -----------------------------------------------------------------------------
# Final Stage: Production Server
# -----------------------------------------------------------------------------
FROM python:3.12-slim

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy installed Python dependencies from builder stage
COPY --from=python-production /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:${PATH}"

# Copy application code
COPY core/ ./core/
COPY manage.py ./
COPY migrations/ ./migrations/ 2>/dev/null || true

# Copy static and templates directories
COPY static/ ./static/ 2>/dev/null || true
COPY templates/ ./templates/ 2>/dev/null || true

# Copy built frontend from node build stage
COPY --from=node-build /app/frontend/dist ./public

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run Gunicorn with 4 workers
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "manage:app"]
