"""
AlgoSwing — Health Check API
GET /api/v1/health — full health check with DB + Telegram status
"""
from fastapi import APIRouter
from loguru import logger

from app.core.database import get_db
from app.alerts.telegram import TelegramAlert
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """Basic liveness check."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "env": settings.app_env,
    }


@router.get("/detailed")
async def detailed_health():
    """Full health check including DB and Telegram connectivity."""
    health = {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "services": {},
    }

    # Check MongoDB
    try:
        db = get_db()
        await db.command("ping")
        health["services"]["mongodb"] = {"status": "ok"}
    except Exception as e:
        health["services"]["mongodb"] = {"status": "error", "detail": str(e)}
        health["status"] = "degraded"

    # Check Telegram
    try:
        tg = TelegramAlert()
        tg_result = await tg.test_connection()
        health["services"]["telegram"] = {
            "status": "ok" if tg_result.get("connected") else "not_configured",
            **tg_result,
        }
    except Exception as e:
        health["services"]["telegram"] = {"status": "error", "detail": str(e)}

    return health
