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
    """Initialize and register all tools"""
    register_weather_tool()
    register_news_tool()
    register_search_tool()


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
