"""
A.B.E.L - Utility Services
QR, URL, Translation, Weather, News
"""

from app.services.utilities.qr_service import QRService
from app.services.utilities.url_service import URLService
from app.services.utilities.translation_service import TranslationService
from app.services.utilities.weather_service import WeatherService
from app.services.utilities.news_service import NewsService
from app.services.utilities.tools_service import ToolsService

__all__ = [
    "QRService", "URLService", "TranslationService",
    "WeatherService", "NewsService", "ToolsService"
]
