"""
A.B.E.L - Weather Service
Integrates OpenWeatherMap, WeatherAPI, Open-Meteo
"""

from typing import Optional, List, Dict, Any
import httpx
from app.core.config import settings
from app.core.logging import logger


class WeatherService:
    """
    Weather service integrating:
    - OpenWeatherMap
    - Open-Meteo (FREE - No auth)
    - WeatherAPI
    """

    OPENWEATHER_API = "https://api.openweathermap.org/data/2.5"
    OPENWEATHER_GEO = "https://api.openweathermap.org/geo/1.0"
    OPEN_METEO_API = "https://api.open-meteo.com/v1"
    WEATHERAPI = "https://api.weatherapi.com/v1"

    def __init__(self):
        self.openweather_key = getattr(settings, 'openweather_api_key', '')
        self.weatherapi_key = getattr(settings, 'weatherapi_key', '')

    # ========================================
    # OPEN-METEO API (FREE - No auth needed)
    # ========================================
    async def openmeteo_current(
        self,
        latitude: float,
        longitude: float,
    ) -> Dict[str, Any]:
        """Get current weather from Open-Meteo"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.OPEN_METEO_API}/forecast",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "current_weather": "true",
                        "hourly": "temperature_2m,relativehumidity_2m,precipitation,windspeed_10m",
                        "timezone": "auto",
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Open-Meteo current error: {e}")
        return {}

    async def openmeteo_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Get weather forecast from Open-Meteo"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.OPEN_METEO_API}/forecast",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,sunrise,sunset,windspeed_10m_max",
                        "timezone": "auto",
                        "forecast_days": days,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Open-Meteo forecast error: {e}")
        return {}

    # ========================================
    # OPENWEATHERMAP API
    # ========================================
    async def openweather_current(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        units: str = "metric",  # metric, imperial
    ) -> Optional[Dict[str, Any]]:
        """Get current weather from OpenWeatherMap"""
        try:
            params = {
                "appid": self.openweather_key,
                "units": units,
                "lang": "fr",
            }
            if city:
                params["q"] = city
            elif lat and lon:
                params["lat"] = lat
                params["lon"] = lon
            else:
                return None

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.OPENWEATHER_API}/weather",
                    params=params,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"OpenWeather current error: {e}")
        return None

    async def openweather_forecast(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        units: str = "metric",
    ) -> Dict[str, Any]:
        """Get 5-day forecast from OpenWeatherMap"""
        try:
            params = {
                "appid": self.openweather_key,
                "units": units,
                "lang": "fr",
            }
            if city:
                params["q"] = city
            elif lat and lon:
                params["lat"] = lat
                params["lon"] = lon

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.OPENWEATHER_API}/forecast",
                    params=params,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"OpenWeather forecast error: {e}")
        return {}

    async def openweather_geocode(self, city: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Geocode city name"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.OPENWEATHER_GEO}/direct",
                    params={
                        "q": city,
                        "limit": limit,
                        "appid": self.openweather_key,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"OpenWeather geocode error: {e}")
        return []

    async def openweather_air_pollution(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """Get air pollution data"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.OPENWEATHER_API}/air_pollution",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.openweather_key,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"OpenWeather air pollution error: {e}")
        return None

    # ========================================
    # HELPER FUNCTIONS
    # ========================================
    async def get_weather(
        self,
        location: str,
        include_forecast: bool = True,
    ) -> Dict[str, Any]:
        """Get comprehensive weather data for a location"""
        # First geocode the location
        geo_results = await self.openweather_geocode(location)

        if not geo_results:
            return {"error": f"Location '{location}' not found"}

        geo = geo_results[0]
        lat, lon = geo["lat"], geo["lon"]

        result = {
            "location": {
                "name": geo.get("name"),
                "country": geo.get("country"),
                "lat": lat,
                "lon": lon,
            }
        }

        # Get current weather
        current = await self.openweather_current(lat=lat, lon=lon)
        if current:
            result["current"] = {
                "temp": current["main"]["temp"],
                "feels_like": current["main"]["feels_like"],
                "humidity": current["main"]["humidity"],
                "pressure": current["main"]["pressure"],
                "description": current["weather"][0]["description"],
                "icon": current["weather"][0]["icon"],
                "wind_speed": current["wind"]["speed"],
                "clouds": current["clouds"]["all"],
            }

        # Get forecast if requested
        if include_forecast:
            forecast = await self.openweather_forecast(lat=lat, lon=lon)
            if forecast and "list" in forecast:
                result["forecast"] = [
                    {
                        "datetime": f["dt_txt"],
                        "temp": f["main"]["temp"],
                        "description": f["weather"][0]["description"],
                        "icon": f["weather"][0]["icon"],
                    }
                    for f in forecast["list"][:8]  # Next 24 hours
                ]

        return result

    def get_weather_emoji(self, code: str) -> str:
        """Get emoji for weather icon code"""
        emoji_map = {
            "01d": "☀️", "01n": "🌙",
            "02d": "⛅", "02n": "☁️",
            "03d": "☁️", "03n": "☁️",
            "04d": "☁️", "04n": "☁️",
            "09d": "🌧️", "09n": "🌧️",
            "10d": "🌦️", "10n": "🌧️",
            "11d": "⛈️", "11n": "⛈️",
            "13d": "❄️", "13n": "❄️",
            "50d": "🌫️", "50n": "🌫️",
        }
        return emoji_map.get(code, "🌡️")

    # Default cities for quick access
    POPULAR_CITIES = [
        {"name": "Paris", "country": "FR", "lat": 48.8566, "lon": 2.3522},
        {"name": "London", "country": "GB", "lat": 51.5074, "lon": -0.1278},
        {"name": "New York", "country": "US", "lat": 40.7128, "lon": -74.0060},
        {"name": "Tokyo", "country": "JP", "lat": 35.6762, "lon": 139.6503},
        {"name": "Sydney", "country": "AU", "lat": -33.8688, "lon": 151.2093},
    ]
