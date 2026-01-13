#!/usr/bin/env python3
"""
Quick startup check - verifies the app can import and initialize.
Run this before deployment to catch import errors.
"""

import sys
import logging
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Check if app can start."""
    logger.info("Checking A.B.E.L. backend startup...")

    try:
        # Import main app
        logger.info("1/5 Importing main application...")
        from app.main import app, settings

        logger.info(f"✓ App imported successfully")
        logger.info(f"  - Name: {settings.app_name}")
        logger.info(f"  - Version: {app.version}")

        # Check settings
        logger.info("\n2/5 Checking settings...")
        logger.info(f"✓ Settings loaded")
        logger.info(f"  - Environment: {settings.app_env}")
        logger.info(f"  - Debug: {settings.debug}")
        logger.info(f"  - Mock mode: {settings.allow_mock_mode}")

        # Check Supabase
        logger.info("\n3/5 Checking Supabase connection...")
        from app.services.supabase.client import get_supabase_client

        supabase = get_supabase_client()
        if supabase.is_available:
            logger.info("✓ Supabase available")
        else:
            logger.warning("⚠ Supabase in mock mode (auth disabled)")

        # Check Gemini
        logger.info("\n4/5 Checking Gemini API...")
        from app.services.gemini.client import get_gemini_client

        gemini = get_gemini_client()
        if gemini.is_available:
            logger.info("✓ Gemini available")
        else:
            logger.warning("⚠ Gemini in mock mode (AI disabled)")

        # Check tools
        logger.info("\n5/5 Checking external tools...")
        from app.services.tools import initialize_tools

        initialize_tools()
        logger.info("✓ Tools initialized")

        # Final status
        logger.info("\n" + "=" * 60)
        logger.info("Startup Check Complete")
        logger.info("=" * 60)

        if supabase.is_available and gemini.is_available:
            logger.info("✓ All services operational - ready for production")
        elif not supabase.is_available and not gemini.is_available:
            logger.warning("⚠ All services in mock mode - development only")
        else:
            logger.warning("⚠ Some services in mock mode - degraded operation")

        logger.info("\nTo start the server:")
        logger.info("  poetry run uvicorn app.main:app --reload")
        logger.info("\nOr for production:")
        logger.info("  poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000")

        return 0

    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        logger.error("\nPossible fixes:")
        logger.error("  1. Install dependencies: poetry install")
        logger.error("  2. Check your Python version: python --version (need 3.11+)")
        logger.error("  3. Activate venv: poetry shell")
        return 1

    except Exception as e:
        logger.error(f"✗ Startup check failed: {e}")
        logger.exception("Full error:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
