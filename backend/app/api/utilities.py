"""
A.B.E.L - Utilities API Routes
Weather, News, Translation, Tools
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import Response
from typing import Optional, List
from app.services.utilities.weather_service import WeatherService
from app.services.utilities.news_service import NewsService
from app.services.utilities.translation_service import TranslationService
from app.services.utilities.tools_service import ToolsService

router = APIRouter(prefix="/utilities", tags=["Utilities"])

# Service instances
weather_service = WeatherService()
news_service = NewsService()
translation_service = TranslationService()
tools_service = ToolsService()


# ========================================
# WEATHER ENDPOINTS
# ========================================
@router.get("/weather/current")
async def get_current_weather(
    city: Optional[str] = Query(None, description="City name"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    units: str = Query("metric", regex="^(metric|imperial)$"),
):
    """Get current weather"""
    if city:
        weather = await weather_service.get_weather_by_city(city, units)
    elif lat is not None and lon is not None:
        weather = await weather_service.get_weather_by_coords(lat, lon, units)
    else:
        raise HTTPException(status_code=400, detail="Provide city or lat/lon")

    if not weather:
        raise HTTPException(status_code=404, detail="Weather data not found")
    return weather


@router.get("/weather/forecast")
async def get_weather_forecast(
    city: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    days: int = Query(5, ge=1, le=16),
    units: str = Query("metric"),
):
    """Get weather forecast"""
    if city:
        forecast = await weather_service.get_forecast_by_city(city, days, units)
    elif lat is not None and lon is not None:
        forecast = await weather_service.get_forecast_by_coords(lat, lon, days, units)
    else:
        raise HTTPException(status_code=400, detail="Provide city or lat/lon")

    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return forecast


@router.get("/weather/air-quality")
async def get_air_quality(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
):
    """Get air quality data"""
    data = await weather_service.get_air_quality(lat, lon)
    if not data:
        raise HTTPException(status_code=404, detail="Air quality data not found")
    return data


# ========================================
# NEWS ENDPOINTS
# ========================================
@router.get("/news/headlines")
async def get_news_headlines(
    country: str = Query("fr", description="Country code"),
    category: Optional[str] = Query(None, description="Category filter"),
    q: Optional[str] = Query(None, description="Search query"),
    page_size: int = Query(20, ge=1, le=100),
):
    """Get top headlines"""
    news = await news_service.newsapi_headlines(country, category, q, page_size)
    return {"articles": news, "count": len(news)}


@router.get("/news/search")
async def search_news(
    q: str = Query(..., description="Search query"),
    from_date: Optional[str] = Query(None, description="From date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="To date (YYYY-MM-DD)"),
    sort_by: str = Query("publishedAt"),
    page_size: int = Query(20, ge=1, le=100),
):
    """Search news articles"""
    news = await news_service.newsapi_search(q, from_date, to_date, sort_by, page_size)
    return {"articles": news, "count": len(news)}


@router.get("/news/tech")
async def get_tech_news(limit: int = Query(20, ge=1, le=50)):
    """Get tech news from multiple sources"""
    news = await news_service.get_tech_news(limit)
    return news


@router.get("/news/hackernews/top")
async def get_hackernews_top(limit: int = Query(30, ge=1, le=100)):
    """Get top stories from Hacker News"""
    stories = await news_service.hackernews_top(limit)
    return {"stories": stories, "count": len(stories)}


@router.get("/news/hackernews/new")
async def get_hackernews_new(limit: int = Query(30, ge=1, le=100)):
    """Get new stories from Hacker News"""
    stories = await news_service.hackernews_new(limit)
    return {"stories": stories, "count": len(stories)}


@router.get("/news/hackernews/best")
async def get_hackernews_best(limit: int = Query(30, ge=1, le=100)):
    """Get best stories from Hacker News"""
    stories = await news_service.hackernews_best(limit)
    return {"stories": stories, "count": len(stories)}


@router.get("/news/reddit/{subreddit}")
async def get_reddit_posts(
    subreddit: str,
    sort: str = Query("hot", regex="^(hot|new|top|rising)$"),
    limit: int = Query(25, ge=1, le=100),
    time: str = Query("day", regex="^(hour|day|week|month|year|all)$"),
):
    """Get posts from a subreddit"""
    posts = await news_service.reddit_subreddit(subreddit, sort, limit, time)
    return {"subreddit": subreddit, "posts": posts, "count": len(posts)}


# ========================================
# TRANSLATION ENDPOINTS
# ========================================
@router.post("/translate")
async def translate_text(
    text: str = Query(..., description="Text to translate"),
    target: str = Query(..., description="Target language code"),
    source: str = Query("auto", description="Source language code"),
):
    """Translate text"""
    result = await translation_service.translate(text, target, source)
    return result


@router.post("/translate/batch")
async def translate_batch(
    texts: List[str],
    target: str = Query(..., description="Target language code"),
    source: str = Query("en", description="Source language code"),
):
    """Translate multiple texts"""
    results = await translation_service.translate_batch(texts, target, source)
    return {"translations": results}


@router.get("/translate/languages")
async def get_translation_languages():
    """Get supported languages"""
    return {"languages": translation_service.get_all_languages()}


# ========================================
# TOOLS ENDPOINTS
# ========================================
@router.get("/tools/qr")
async def generate_qr_code(
    data: str = Query(..., description="Data to encode"),
    size: int = Query(200, ge=50, le=1000),
    format: str = Query("png", regex="^(png|gif|jpeg|svg)$"),
):
    """Generate QR code image"""
    qr_bytes = await tools_service.generate_qr(data, size, format)
    if not qr_bytes:
        raise HTTPException(status_code=500, detail="QR generation failed")

    media_type = f"image/{format}" if format != "svg" else "image/svg+xml"
    return Response(content=qr_bytes, media_type=media_type)


@router.get("/tools/qr/url")
async def get_qr_url(
    data: str = Query(..., description="Data to encode"),
    size: int = Query(200, ge=50, le=1000),
):
    """Get QR code URL (no download)"""
    url = tools_service.get_qr_url(data, size)
    return {"url": url}


@router.get("/tools/shorten")
async def shorten_url(url: str = Query(..., description="URL to shorten")):
    """Shorten a URL"""
    short = await tools_service.shorten_url(url)
    if not short:
        raise HTTPException(status_code=500, detail="URL shortening failed")
    return {"original": url, "shortened": short}


@router.get("/tools/password")
async def generate_password(
    length: int = Query(16, ge=8, le=128),
    uppercase: bool = Query(True),
    lowercase: bool = Query(True),
    digits: bool = Query(True),
    special: bool = Query(True),
    exclude_ambiguous: bool = Query(False),
):
    """Generate a secure password"""
    password = tools_service.generate_password(
        length, uppercase, lowercase, digits, special, exclude_ambiguous
    )
    return {"password": password, "length": len(password)}


@router.get("/tools/passphrase")
async def generate_passphrase(
    words: int = Query(4, ge=3, le=10),
    separator: str = Query("-"),
):
    """Generate a passphrase"""
    passphrase = tools_service.generate_passphrase(words, separator)
    return {"passphrase": passphrase}


@router.post("/tools/password/check")
async def check_password_strength(password: str):
    """Check password strength"""
    result = tools_service.check_password_strength(password)
    return result


@router.get("/tools/hash")
async def hash_text(
    text: str = Query(..., description="Text to hash"),
    algorithm: str = Query("sha256", regex="^(md5|sha1|sha256|sha512)$"),
):
    """Generate hash of text"""
    hash_value = tools_service.hash_text(text, algorithm)
    return {"text": text, "algorithm": algorithm, "hash": hash_value}


@router.get("/tools/base64/encode")
async def base64_encode(text: str = Query(..., description="Text to encode")):
    """Encode text to base64"""
    encoded = tools_service.base64_encode(text)
    return {"original": text, "encoded": encoded}


@router.get("/tools/base64/decode")
async def base64_decode(text: str = Query(..., description="Base64 to decode")):
    """Decode base64 to text"""
    decoded = tools_service.base64_decode(text)
    return {"encoded": text, "decoded": decoded}


@router.get("/tools/convert/temperature")
async def convert_temperature(
    value: float = Query(..., description="Temperature value"),
    from_unit: str = Query(..., alias="from", regex="^[CFK]$"),
    to_unit: str = Query(..., alias="to", regex="^[CFK]$"),
):
    """Convert temperature between C, F, K"""
    result = tools_service.convert_temperature(value, from_unit, to_unit)
    return {"value": value, "from": from_unit, "to": to_unit, "result": result}


@router.get("/tools/convert/length")
async def convert_length(
    value: float = Query(..., description="Length value"),
    from_unit: str = Query(..., alias="from"),
    to_unit: str = Query(..., alias="to"),
):
    """Convert length between units"""
    result = tools_service.convert_length(value, from_unit, to_unit)
    return {"value": value, "from": from_unit, "to": to_unit, "result": result}


@router.get("/tools/convert/weight")
async def convert_weight(
    value: float = Query(..., description="Weight value"),
    from_unit: str = Query(..., alias="from"),
    to_unit: str = Query(..., alias="to"),
):
    """Convert weight between units"""
    result = tools_service.convert_weight(value, from_unit, to_unit)
    return {"value": value, "from": from_unit, "to": to_unit, "result": result}


@router.post("/tools/text/analyze")
async def analyze_text(text: str):
    """Analyze text statistics"""
    result = tools_service.analyze_text(text)
    return result


@router.post("/tools/text/frequency")
async def word_frequency(
    text: str,
    top_n: int = Query(10, ge=1, le=100),
):
    """Count word frequency in text"""
    result = tools_service.count_word_frequency(text, top_n)
    return {"words": result}


@router.get("/tools/time")
async def get_timezone_time(timezone: str = Query("Europe/Paris")):
    """Get current time in a timezone"""
    time = tools_service.get_timezone_time(timezone)
    return {"timezone": timezone, "time": time}


@router.get("/tools/date/diff")
async def date_difference(
    date1: str = Query(..., description="First date (YYYY-MM-DD)"),
    date2: str = Query(..., description="Second date (YYYY-MM-DD)"),
):
    """Calculate difference between two dates"""
    result = tools_service.calculate_date_diff(date1, date2)
    return result
