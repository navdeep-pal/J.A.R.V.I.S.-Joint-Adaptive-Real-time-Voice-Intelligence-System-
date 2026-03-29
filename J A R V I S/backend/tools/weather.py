"""
backend/tools/weather.py

Provides live weather and location detection tools for the J.A.R.V.I.S. agent.
"""
import os
import asyncio
import requests
import logging
from dotenv import load_dotenv
from config import ConfigManager

config = ConfigManager()

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_current_city() -> str:
    """Detect the user's city via IP lookup (non-blocking)."""
    try:
        def _fetch():
            response = requests.get("https://ipinfo.io", timeout=5)
            return response.json().get("city", "Unknown")
        return await asyncio.to_thread(_fetch)
    except Exception:
        return "Unknown"


async def get_weather(city: str = "") -> str:
    """
    Gives current weather information for a given city.

    Use this tool when the user asks about weather, rain, temperature, humidity, or wind.
    If no city is given, detect city automatically.

    Example prompts:
    - "आज का मौसम कैसा है?"
    - "Weather बताओ Saharanpur का"
    - "क्या बारिश होगी Saharanpur में?"
    """
    api_key = config.get_api_key("openweather") or os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        logger.error("OpenWeather API key missing.")
        return "OpenWeather API key not found in configuration."

    if not city:
        city = await get_current_city()

    logger.info(f"Fetching weather for city: {city}")

    def _fetch_weather():
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric"
        }
        return requests.get(url, params=params, timeout=10)

    try:
        response = await asyncio.to_thread(_fetch_weather)
        if response.status_code != 200:
            logger.error(f"OpenWeather API error: {response.status_code} - {response.text}")
            return f"Error: Could not fetch weather for {city}. Please check the city name."

        data = response.json()
        weather = data["weather"][0]["description"].title()
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        result = (
            f"Weather in {city}:\n"
            f"- Condition: {weather}\n"
            f"- Temperature: {temperature}°C\n"
            f"- Humidity: {humidity}%\n"
            f"- Wind Speed: {wind_speed} m/s"
        )

        logger.info(f"Weather result:\n{result}")
        return result

    except Exception as e:
        logger.exception(f"Exception while fetching weather: {e}")
        return "An error occurred while fetching weather."
