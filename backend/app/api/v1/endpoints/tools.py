"""
=============================================================================
TOOLS API ENDPOINTS
=============================================================================
A.B.E.L. Project - External Tools API (Weather, News, Search)
=============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.core.security.rate_limiter import limiter
from app.core.security.auth import get_current_user
from app.services.tools import (
    get_tool_registry,
    get_weather,
    get_news,
    get_headlines,
    web_search,
    quick_answer
)

router = APIRouter(prefix="/tools", tags=["tools"])


# =============================================================================
# SCHEMAS
# =============================================================================

class WeatherRequest(BaseModel):
    city: str = Field(..., min_length=1, description="City name")
    latitude: Optional[float] = Field(None, description="Custom latitude")
    longitude: Optional[float] = Field(None, description="Custom longitude")


class NewsRequest(BaseModel):
    category: str = Field("france", description="News category")
    source: Optional[str] = Field(None, description="Specific source")
    limit: int = Field(5, ge=1, le=10, description="Number of articles")
    search: Optional[str] = Field(None, description="Search filter")


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Search query")
    limit: int = Field(5, ge=1, le=10, description="Number of results")
    region: str = Field("fr-fr", description="Region code")


class ToolExecuteRequest(BaseModel):
    tool_name: str = Field(..., description="Tool name to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")


class ToolResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/available", response_model=Dict[str, Any])
@limiter.limit("60/minute")
async def list_available_tools(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    List all available tools

    Returns tool names, descriptions, and categories
    """
    registry = get_tool_registry()
    tools = registry.get_all_tools()

    return {
        "tools": [
            {
                "name": t.name,
                "description": t.description,
                "category": t.category.value,
                "parameters": t.parameters,
                "rate_limit": t.rate_limit
            }
            for t in tools
        ],
        "count": len(tools)
    }


@router.post("/execute", response_model=ToolResponse)
@limiter.limit("30/minute")
async def execute_tool(
    http_request: Request,
    request: ToolExecuteRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Execute a tool by name with parameters

    Generic endpoint for any registered tool
    """
    registry = get_tool_registry()
    result = await registry.execute(request.tool_name, request.parameters)

    if result.get("success"):
        return ToolResponse(success=True, data=result.get("result"))
    else:
        return ToolResponse(success=False, error=result.get("error"))


@router.get("/gemini-functions", response_model=List[Dict[str, Any]])
@limiter.limit("60/minute")
async def get_gemini_function_declarations(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Get tool definitions in Gemini function calling format

    Use this to integrate tools with Gemini chat
    """
    registry = get_tool_registry()
    return registry.get_gemini_function_declarations()


# =============================================================================
# WEATHER ENDPOINTS
# =============================================================================

@router.get("/weather", response_model=ToolResponse)
@limiter.limit("30/minute")
async def get_weather_endpoint(
    request: Request,
    city: str = Query(..., min_length=1, description="City name"),
    latitude: Optional[float] = Query(None, description="Custom latitude"),
    longitude: Optional[float] = Query(None, description="Custom longitude"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current weather and forecast for a city

    Uses Open-Meteo API (free, no key required)
    """
    result = await get_weather(city, latitude, longitude)

    if "error" in result:
        return ToolResponse(success=False, error=result["error"])

    return ToolResponse(success=True, data=result)


@router.post("/weather", response_model=ToolResponse)
@limiter.limit("30/minute")
async def post_weather_endpoint(
    http_request: Request,
    request: WeatherRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Get current weather and forecast for a city (POST)
    """
    result = await get_weather(request.city, request.latitude, request.longitude)

    if "error" in result:
        return ToolResponse(success=False, error=result["error"])

    return ToolResponse(success=True, data=result)


# =============================================================================
# NEWS ENDPOINTS
# =============================================================================

@router.get("/news", response_model=ToolResponse)
@limiter.limit("20/minute")
async def get_news_endpoint(
    request: Request,
    category: str = Query("france", description="News category"),
    source: Optional[str] = Query(None, description="Specific source"),
    limit: int = Query(5, ge=1, le=10, description="Number of articles"),
    search: Optional[str] = Query(None, description="Search filter"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get latest news by category

    Categories: france, tech, international, science
    Uses free RSS feeds
    """
    result = await get_news(category, source, limit, search)

    if "error" in result:
        return ToolResponse(success=False, error=result["error"])

    return ToolResponse(success=True, data=result)


@router.post("/news", response_model=ToolResponse)
@limiter.limit("20/minute")
async def post_news_endpoint(
    http_request: Request,
    request: NewsRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Get latest news by category (POST)
    """
    result = await get_news(request.category, request.source, request.limit, request.search)

    if "error" in result:
        return ToolResponse(success=False, error=result["error"])

    return ToolResponse(success=True, data=result)


@router.get("/headlines", response_model=ToolResponse)
@limiter.limit("10/minute")
async def get_headlines_endpoint(
    request: Request,
    limit: int = Query(5, ge=1, le=5, description="Articles per category"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get top headlines from all categories

    Quick overview of current news
    """
    result = await get_headlines(limit)

    return ToolResponse(success=True, data=result)


# =============================================================================
# SEARCH ENDPOINTS
# =============================================================================

@router.get("/search", response_model=ToolResponse)
@limiter.limit("20/minute")
async def search_endpoint(
    request: Request,
    query: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(5, ge=1, le=10, description="Number of results"),
    region: str = Query("fr-fr", description="Region code"),
    current_user: dict = Depends(get_current_user)
):
    """
    Search the web using DuckDuckGo

    Free, no API key required
    """
    result = await web_search(query, limit, region)

    if "error" in result:
        return ToolResponse(success=False, error=result["error"])

    return ToolResponse(success=True, data=result)


@router.post("/search", response_model=ToolResponse)
@limiter.limit("20/minute")
async def post_search_endpoint(
    http_request: Request,
    request: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Search the web (POST)
    """
    result = await web_search(request.query, request.limit, request.region)

    if "error" in result:
        return ToolResponse(success=False, error=result["error"])

    return ToolResponse(success=True, data=result)


@router.get("/answer", response_model=ToolResponse)
@limiter.limit("30/minute")
async def quick_answer_endpoint(
    request: Request,
    query: str = Query(..., min_length=2, description="Question or query"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a quick answer for a factual question

    Works well for definitions, conversions, calculations
    """
    result = await quick_answer(query)

    return ToolResponse(success=True, data=result)
