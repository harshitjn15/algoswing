"""
AlgoSwing Backend — Logging configuration via loguru
"""
import sys
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Configure loguru with structured output."""
    logger.remove()  # Remove default handler

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
        "<level>{message}</level>"
    )

    # Console
    logger.add(
        sys.stdout,
        format=log_format,
        level="DEBUG" if settings.debug else "INFO",
        colorize=True,
        enqueue=True,
    )

    # File — rotates daily, keeps 30 days
    logger.add(
        "logs/algoswing_{time:YYYY-MM-DD}.log",
        format=log_format,
        level="INFO",
        rotation="00:00",
        retention="30 days",
        compression="gz",
        enqueue=True,
    )

    logger.info(f"✅ Logging initialized [{settings.app_env}]")


__all__ = ["logger", "setup_logging"]
