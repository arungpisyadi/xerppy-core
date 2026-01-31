"""Backend entry point - starts the FastAPI server"""
import uvicorn

from app.config.settings import settings


def main():
    """Start the FastAPI development server"""
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
