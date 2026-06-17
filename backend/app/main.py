"""
AlgoSwing Backend — FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.database import connect_db, close_db
from app.core.scheduler import setup_scheduler
from app.strategies.registry import load_all_strategies
from app.api.router import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # ── Startup ────────────────────────────────────────
    setup_logging()
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version} [{settings.app_env}]")

    # Connect to MongoDB
    await connect_db()

    # Load strategy plugins
    load_all_strategies()

    # Start APScheduler
    scheduler = setup_scheduler()
    scheduler.start()
    logger.info("⏰ Scheduler started")

    yield  # Application is running

    # ── Shutdown ───────────────────────────────────────
    logger.info("🛑 Shutting down AlgoSwing...")
    scheduler.shutdown(wait=False)
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Production-grade algorithmic swing trading platform. "
            "Scans Chartink, detects IPO ATH retest setups, sends Telegram alerts."
        ),
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # ── Middleware ─────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ── Routes ─────────────────────────────────────────
    app.include_router(api_router)

    # Root redirect
    @app.get("/", tags=["root"])
    async def root():
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
        }

    # ── Exception Handlers ─────────────────────────────
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTP Exception {exc.status_code}: {exc.detail} at {request.url}")
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation Error: {exc.errors()} at {request.url}")
        return JSONResponse(status_code=422, content={"detail": "Validation Error", "errors": exc.errors()})

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled Exception: {exc} at {request.url}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

    logger.info("✅ FastAPI app created")
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
