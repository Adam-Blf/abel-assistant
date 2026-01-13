"""
=============================================================================
TOOLS SERVICES - External Tools for Gemini Function Calling
=============================================================================
A.B.E.L. Project - Weather, News, Web Search
=============================================================================
"""

from app.services.tools.registry import (
    ToolRegistry,
    ToolDefinition,
    ToolCategory,
    get_tool_registry
)
from app.services.tools.weather import get_weather, register_weather_tool
from app.services.tools.news import get_news, get_headlines, register_news_tool
from app.services.tools.web_search import web_search, quick_answer, register_search_tool


def initialize_tools():
    """
    Initialize and register all tools.
    Never crashes - catches all errors and continues.
    """
    import logging
    logger = logging.getLogger(__name__)

    tools_initialized = []
    tools_failed = []

    # Weather tool
    try:
        register_weather_tool()
        tools_initialized.append("weather")
    except Exception as e:
        logger.error(f"Failed to initialize weather tool: {e}")
        tools_failed.append("weather")

    # News tool
    try:
        register_news_tool()
        tools_initialized.append("news")
    except Exception as e:
        logger.error(f"Failed to initialize news tool: {e}")
        tools_failed.append("news")

    # Search tool
    try:
        register_search_tool()
        tools_initialized.append("search")
    except Exception as e:
        logger.error(f"Failed to initialize search tool: {e}")
        tools_failed.append("search")

    logger.info(f"Tools initialized: {tools_initialized}")
    if tools_failed:
        logger.warning(f"Tools failed: {tools_failed}")


__all__ = [
    # Registry
    "ToolRegistry",
    "ToolDefinition",
    "ToolCategory",
    "get_tool_registry",
    # Weather
    "get_weather",
    "register_weather_tool",
    # News
    "get_news",
    "get_headlines",
    "register_news_tool",
    # Search
    "web_search",
    "quick_answer",
    "register_search_tool",
    # Init
    "initialize_tools",
]
