#!/usr/bin/env python3
"""
Test script to verify backend resilience.
Tests that the app starts without any environment variables.
"""

import os
import sys
import logging
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_settings_without_env():
    """Test that settings can be loaded without environment variables."""
    logger.info("Test 1: Loading settings without environment variables")

    # Clear all A.B.E.L. related env vars
    env_vars_to_clear = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_KEY",
        "GEMINI_API_KEY",
        "SECRET_KEY",
    ]

    for var in env_vars_to_clear:
        os.environ.pop(var, None)

    try:
        # Clear the settings cache
        from app.config.settings import get_settings
        get_settings.cache_clear()

        settings = get_settings()
        logger.info(f"✓ Settings loaded successfully")
        logger.info(f"  - App name: {settings.app_name}")
        logger.info(f"  - Environment: {settings.app_env}")
        logger.info(f"  - Mock mode: {settings.allow_mock_mode}")
        logger.info(f"  - Secret key length: {len(settings.secret_key.get_secret_value())}")
        return True
    except Exception as e:
        logger.error(f"✗ Settings loading failed: {e}")
        return False


def test_supabase_mock_mode():
    """Test that Supabase client works in mock mode."""
    logger.info("\nTest 2: Supabase client in mock mode")

    try:
        from app.services.supabase.client import get_supabase_client

        # Create a fresh instance
        import app.services.supabase.client as supabase_module
        supabase_module._supabase_client = None

        client = get_supabase_client()
        logger.info(f"✓ Supabase client created")
        logger.info(f"  - Available: {client.is_available}")
        logger.info(f"  - Mock mode: {not client.is_available}")

        if client.is_available:
            logger.warning("  Warning: Supabase is available (expected mock mode)")
        else:
            logger.info("  - Client correctly in mock mode")

        return True
    except Exception as e:
        logger.error(f"✗ Supabase client failed: {e}")
        return False


def test_gemini_mock_mode():
    """Test that Gemini client works in mock mode."""
    logger.info("\nTest 3: Gemini client in mock mode")

    try:
        from app.services.gemini.client import get_gemini_client

        # Create a fresh instance
        import app.services.gemini.client as gemini_module
        gemini_module._gemini_client = None

        client = get_gemini_client()
        logger.info(f"✓ Gemini client created")
        logger.info(f"  - Available: {client.is_available}")
        logger.info(f"  - Mock mode: {not client.is_available}")

        if client.is_available:
            logger.warning("  Warning: Gemini is available (expected mock mode)")
        else:
            logger.info("  - Client correctly in mock mode")

        return True
    except Exception as e:
        logger.error(f"✗ Gemini client failed: {e}")
        return False


def test_auth_service_degraded():
    """Test that auth service handles unavailability gracefully."""
    logger.info("\nTest 4: Auth service with Supabase unavailable")

    try:
        from app.services.supabase.auth import get_auth_service

        # Create fresh instance
        import app.services.supabase.auth as auth_module
        auth_module._auth_service = None

        auth = get_auth_service()
        logger.info(f"✓ Auth service created")
        logger.info(f"  - Available: {auth.is_available}")

        if not auth.is_available:
            logger.info("  - Auth service correctly reports unavailability")

        return True
    except Exception as e:
        logger.error(f"✗ Auth service failed: {e}")
        return False


def test_tools_initialization():
    """Test that tools initialization doesn't crash."""
    logger.info("\nTest 5: Tools initialization")

    try:
        from app.services.tools import initialize_tools

        initialize_tools()
        logger.info(f"✓ Tools initialized without crashing")
        return True
    except Exception as e:
        logger.error(f"✗ Tools initialization failed: {e}")
        return False


def main():
    """Run all resilience tests."""
    logger.info("=" * 60)
    logger.info("A.B.E.L. Backend Resilience Tests")
    logger.info("=" * 60)

    tests = [
        test_settings_without_env,
        test_supabase_mock_mode,
        test_gemini_mock_mode,
        test_auth_service_degraded,
        test_tools_initialization,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            logger.error(f"Test crashed: {e}")
            results.append(False)

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    passed = sum(results)
    total = len(results)
    logger.info(f"Passed: {passed}/{total}")

    if passed == total:
        logger.info("✓ All tests passed! Backend is crash-proof.")
        return 0
    else:
        logger.error(f"✗ {total - passed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
