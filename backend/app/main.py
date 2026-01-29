"""FastAPI Application Entry Point"""
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config.settings import settings
from app.db.connection import init_db, close_db
from app.modules.auth.router import auth_router
from app.modules.auth.service import AuthService

# Import AI router (optional - CrewAI dependencies)
try:
    from app.modules.ai.router import router as ai_router
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    ai_router = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await init_db()
    
    # Seed default roles and permissions
    async with AsyncSessionLocal() as session:
        await AuthService.seed_default_roles_and_permissions(session)
    
    yield
    
    # Shutdown
    await close_db()


# Static files directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


# Import AsyncSessionLocal for startup
from app.db.connection import AsyncSessionLocal

app = FastAPI(
    title="Xerppy API",
    description="Laravel-like FastAPI Starter Kit with Modular Monolith Architecture",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")

# Include AI router if CrewAI is available
if ai_router is not None:
    app.include_router(ai_router, prefix="/api/v1")
else:
    @app.get("/api/v1/ai/health")
    async def ai_health_check():
        """AI module health check (AI module not available)"""
        return {
            "status": "unavailable",
            "message": "AI module requires CrewAI dependencies. Install with: pip install crewai crewai-tools",
        }

# Mount static files if directory exists
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# SPA fallback - serve index.html for non-API routes
@app.get("/{path:path}")
async def serve_spa(request: Request, path: str):
    """Serve React SPA for non-API routes (React Router support)"""
    # Skip API routes
    if path.startswith("api/"):
        return {"error": "Not found", "detail": f"Route /api/{path} not found"}
    
    # Serve index.html for SPA routes
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"error": "Not found", "detail": f"Route /{path} not found"}


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "healthy",
        "message": "Welcome to Xerppy API",
        "version": "0.1.0",
        "ai_available": AI_AVAILABLE,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug,
    )
