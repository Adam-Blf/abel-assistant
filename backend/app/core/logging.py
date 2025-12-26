"""
A.B.E.L - Logging Configuration
"""

import sys
from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    """Configure application logging with Loguru."""

    # Remove default handler
    logger.remove()

    # Console handler with rich formatting
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        format=log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=settings.debug,
    )

    # File handler for production
    if settings.is_production:
        logger.add(
            "logs/abel_{time:YYYY-MM-DD}.log",
            rotation="1 day",
            retention="30 days",
            compression="gz",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        )

    logger.info(f"🤖 A.B.E.L Logging initialized - Level: {settings.log_level}")


# Initialize logging on import
setup_logging()

__all__ = ["logger"]
