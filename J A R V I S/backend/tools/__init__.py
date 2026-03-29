"""
backend/tools/__init__.py

Exports all available tool functions for easy import by the agent.
"""
from .weather import get_weather, get_current_city
from .google_search import google_search, get_current_datetime

__all__ = [
    "get_weather",
    "get_current_city",
    "google_search",
    "get_current_datetime",
]
