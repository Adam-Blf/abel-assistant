"""
=============================================================================
WEATHER TOOL - Weather Information Service
=============================================================================
A.B.E.L. Project - Weather data using Open-Meteo API (free, no key required)
=============================================================================
"""

import httpx
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from app.services.tools.registry import (
    ToolDefinition,
    ToolCategory,
    get_tool_registry
)

logger = logging.getLogger(__name__)

# Weather code descriptions
WEATHER_CODES = {
    0: "Ciel dégagé",
    1: "Principalement dégagé",
    2: "Partiellement nuageux",
    3: "Couvert",
    45: "Brouillard",
    48: "Brouillard givrant",
    51: "Bruine légère",
    53: "Bruine modérée",
    55: "Bruine dense",
    61: "Pluie légère",
    63: "Pluie modérée",
    65: "Pluie forte",
    71: "Neige légère",
    73: "Neige modérée",
    75: "Neige forte",
    77: "Grains de neige",
    80: "Averses légères",
    81: "Averses modérées",
    82: "Averses violentes",
    85: "Averses de neige légères",
    86: "Averses de neige fortes",
    95: "Orage",
    96: "Orage avec grêle légère",
    99: "Orage avec grêle forte"
}

# City coordinates (expandable)
CITY_COORDINATES = {
    "paris": {"lat": 48.8566, "lon": 2.3522, "name": "Paris"},
    "lyon": {"lat": 45.7640, "lon": 4.8357, "name": "Lyon"},
    "marseille": {"lat": 43.2965, "lon": 5.3698, "name": "Marseille"},
    "toulouse": {"lat": 43.6047, "lon": 1.4442, "name": "Toulouse"},
    "bordeaux": {"lat": 44.8378, "lon": -0.5792, "name": "Bordeaux"},
    "lille": {"lat": 50.6292, "lon": 3.0573, "name": "Lille"},
    "nice": {"lat": 43.7102, "lon": 7.2620, "name": "Nice"},
    "nantes": {"lat": 47.2184, "lon": -1.5536, "name": "Nantes"},
    "strasbourg": {"lat": 48.5734, "lon": 7.7521, "name": "Strasbourg"},
    "montpellier": {"lat": 43.6110, "lon": 3.8767, "name": "Montpellier"},
    "london": {"lat": 51.5074, "lon": -0.1278, "name": "Londres"},
    "new york": {"lat": 40.7128, "lon": -74.0060, "name": "New York"},
    "tokyo": {"lat": 35.6762, "lon": 139.6503, "name": "Tokyo"},
    "berlin": {"lat": 52.5200, "lon": 13.4050, "name": "Berlin"},
    "madrid": {"lat": 40.4168, "lon": -3.7038, "name": "Madrid"},
    "rome": {"lat": 41.9028, "lon": 12.4964, "name": "Rome"},
    "amsterdam": {"lat": 52.3676, "lon": 4.9041, "name": "Amsterdam"},
    "bruxelles": {"lat": 50.8503, "lon": 4.3517, "name": "Bruxelles"},
    "geneve": {"lat": 46.2044, "lon": 6.1432, "name": "Genève"},
    "montreal": {"lat": 45.5017, "lon": -73.5673, "name": "Montréal"},
}


async def get_weather(
    city: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> Dict[str, Any]:
    """
    Get current weather for a city or coordinates

    Args:
        city: City name (e.g., "Paris", "Lyon")
        latitude: Optional latitude for custom location
        longitude: Optional longitude for custom location

    Returns:
        Weather information dict
    """
    logger.info(f"[WeatherTool] Getting weather for: {city}")

    # Resolve coordinates
    if latitude is not None and longitude is not None:
        lat, lon = latitude, longitude
        city_name = city or "Position personnalisée"
    else:
        city_lower = city.lower().strip()
        if city_lower in CITY_COORDINATES:
            coords = CITY_COORDINATES[city_lower]
            lat, lon = coords["lat"], coords["lon"]
            city_name = coords["name"]
        else:
            # Try geocoding with Open-Meteo
            geocode_result = await _geocode_city(city)
            if geocode_result:
                lat = geocode_result["lat"]
                lon = geocode_result["lon"]
                city_name = geocode_result["name"]
            else:
                return {
                    "error": f"Ville '{city}' non trouvée. Essayez avec des coordonnées."
                }

    # Fetch weather data
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "apparent_temperature",
                        "weather_code",
                        "wind_speed_10m",
                        "wind_direction_10m",
                        "pressure_msl",
                        "uv_index"
                    ],
                    "daily": [
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "weather_code",
                        "precipitation_probability_max"
                    ],
                    "timezone": "auto",
                    "forecast_days": 3
                }
            )
            response.raise_for_status()
            data = response.json()

        # Parse current weather
        current = data.get("current", {})
        weather_code = current.get("weather_code", 0)

        result = {
            "city": city_name,
            "coordinates": {"latitude": lat, "longitude": lon},
            "timezone": data.get("timezone", "UTC"),
            "current": {
                "temperature": current.get("temperature_2m"),
                "feels_like": current.get("apparent_temperature"),
                "humidity": current.get("relative_humidity_2m"),
                "wind_speed": current.get("wind_speed_10m"),
                "wind_direction": current.get("wind_direction_10m"),
                "pressure": current.get("pressure_msl"),
                "uv_index": current.get("uv_index"),
                "condition": WEATHER_CODES.get(weather_code, "Inconnu"),
                "condition_code": weather_code
            },
            "forecast": []
        }

        # Parse forecast
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        for i, date in enumerate(dates):
            forecast_code = daily.get("weather_code", [])[i] if i < len(daily.get("weather_code", [])) else 0
            result["forecast"].append({
                "date": date,
                "temp_max": daily.get("temperature_2m_max", [])[i] if i < len(daily.get("temperature_2m_max", [])) else None,
                "temp_min": daily.get("temperature_2m_min", [])[i] if i < len(daily.get("temperature_2m_min", [])) else None,
                "precipitation_chance": daily.get("precipitation_probability_max", [])[i] if i < len(daily.get("precipitation_probability_max", [])) else None,
                "condition": WEATHER_CODES.get(forecast_code, "Inconnu")
            })

        # Generate summary
        temp = current.get("temperature_2m", "N/A")
        condition = WEATHER_CODES.get(weather_code, "Inconnu")
        result["summary"] = f"À {city_name}, il fait actuellement {temp}°C avec {condition.lower()}."

        logger.info(f"[WeatherTool] Weather fetched successfully for {city_name}")
        return result

    except httpx.HTTPError as e:
        logger.error(f"[WeatherTool] HTTP error: {e}")
        return {"error": f"Erreur de connexion au service météo: {str(e)}"}
    except Exception as e:
        logger.error(f"[WeatherTool] Error: {e}")
        return {"error": f"Erreur lors de la récupération météo: {str(e)}"}


async def _geocode_city(city: str) -> Optional[Dict[str, Any]]:
    """Geocode a city name using Open-Meteo geocoding API"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={
                    "name": city,
                    "count": 1,
                    "language": "fr"
                }
            )
            response.raise_for_status()
            data = response.json()

        results = data.get("results", [])
        if results:
            r = results[0]
            return {
                "lat": r["latitude"],
                "lon": r["longitude"],
                "name": r.get("name", city)
            }
        return None

    except Exception as e:
        logger.error(f"[WeatherTool] Geocoding error: {e}")
        return None


def register_weather_tool():
    """Register the weather tool with the registry"""
    registry = get_tool_registry()

    tool = ToolDefinition(
        name="get_weather",
        description="Obtient la météo actuelle et les prévisions pour une ville ou des coordonnées GPS. Utilise l'API Open-Meteo gratuite.",
        category=ToolCategory.WEATHER,
        parameters={
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Nom de la ville (ex: 'Paris', 'Lyon', 'New York')"
                },
                "latitude": {
                    "type": "number",
                    "description": "Latitude optionnelle pour une position personnalisée"
                },
                "longitude": {
                    "type": "number",
                    "description": "Longitude optionnelle pour une position personnalisée"
                }
            },
            "required": ["city"]
        },
        handler=get_weather,
        rate_limit=30
    )

    registry.register(tool)
    logger.info("[WeatherTool] Weather tool registered")
