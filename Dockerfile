# Stage 1: Build Frontend (Node)
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build production bundle
RUN npm run build

# Stage 2: Setup Python Environment
FROM python:3.11-alpine AS backend-build

WORKDIR /app/backend

# Copy Python dependencies
COPY backend/pyproject.toml backend/uv.lock ./

# Install uv package manager
RUN pip install --no-cache uv

# Install dependencies
RUN uv sync --frozen --no-dev

# Stage 3: Final Image (Minimal)
FROM python:3.11-slim AS production

WORKDIR /app

# Copy only installed files from Stage 2
COPY --from=backend-build /app/backend/.venv /app/backend/.venv

# Copy backend source code
COPY backend/ /app/backend

# Copy frontend build from Stage 1 to static folder
COPY --from=frontend-build /app/frontend/dist /app/backend/app/static

# Set environment variables
ENV PATH="/app/backend/.venv/bin:$PATH"
ENV PYTHONPATH="/app/backend"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create static directory if not exists
RUN mkdir -p /app/backend/app/static

# Expose port
EXPOSE 8003

# Switch to non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser

# Run uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
