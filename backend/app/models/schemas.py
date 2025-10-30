from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LocationInput(BaseModel):
    """User's location input."""
    location: Optional[str] = Field(
        None, 
        description="Address, city, or coordinates. If null, uses default test location.",
        examples=["New York, NY", "90210", "Brooklyn"]
    )


class Coordinates(BaseModel):
    """Geographic coordinates."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    location_name: str = Field(..., description="Resolved location name")


class CurrentWeather(BaseModel):
    """Current weather conditions."""
    timestamp: datetime
    temperature: float = Field(..., description="Temperature in Celsius")
    precipitation: float = Field(..., description="Precipitation in mm")
    wind_speed: float = Field(..., description="Wind speed in km/h")
    humidity: float = Field(..., description="Relative humidity in %")
    uv_index: float = Field(..., description="UV index (0-11+)")


class WeatherSuggestion(BaseModel):
    """AI-generated suggestion based on weather."""
    rule_triggered: str = Field(..., description="Which rule triggered this suggestion")
    severity: str = Field(..., description="low | moderate | high")
    suggestion: str = Field(..., description="Human-readable advice")
    icon: str = Field(..., description="Emoji or icon identifier")


class WeatherResponse(BaseModel):
    """Complete weather response with suggestions."""
    location: Coordinates
    current_weather: CurrentWeather
    suggestions: list[WeatherSuggestion]
    timestamp: datetime