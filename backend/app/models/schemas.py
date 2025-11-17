from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LocationInput(BaseModel):
    """User's location input."""
    location: Optional[str] = Field(
        None, 
        description="Address, city, or coordinates. If null, uses default test location.",
        examples=["Brooklyn, NY", "90210", "Central Park"]
    )


class Coordinates(BaseModel):
    """Resolved geographic coordinates."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    location_name: str = Field(..., description="Full resolved location name")
    confidence: Optional[str] = Field(
        "high",
        description="Geocoding confidence: high | medium | low"
    )

class LocationOption(BaseModel):
    """A potential location match for disambiguation."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    location_name: str = Field(..., description="Full display name")
    short_name: str = Field(..., description="Short name (e.g., 'Brooklyn, NY')")
    confidence: str = Field(..., description="high | medium | low")
    location_type: str = Field(..., description="Type: city, state, country, etc.")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 40.6782,
                "longitude": -73.9442,
                "location_name": "Brooklyn, Kings County, New York, United States",
                "short_name": "Brooklyn, NY",
                "confidence": "high",
                "location_type": "city"
            }
        }


class LocationDisambiguationResponse(BaseModel):
    """Response when multiple locations match the query."""
    query: str = Field(..., description="Original search query")
    matches: list[LocationOption] = Field(..., description="Potential location matches")
    is_ambiguous: bool = Field(..., description="True if multiple good matches found")

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
    query: str = Field(..., description="Original user query")
    location: Coordinates
    current_weather: CurrentWeather
    suggestions: list[WeatherSuggestion]
    timestamp: datetime

#RAG USER Prererence and Logging Models

class UserPreference(BaseModel):
    """User preference storage for RAG preparation."""
    user_id: str = Field(..., description="User identifier (session ID for now)")
    preference_type: str = Field(..., description="temp_unit, language, theme, etc.")
    value: str = Field(..., description="Preference value")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    context: Optional[str] = Field(None, description="Context when preference was set")


class LocationLog(BaseModel):
    """Location access logging for pattern detection (Phase 3: RAG)."""
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    latitude: float
    longitude: float
    location_name: str
    location_type: Optional[str] = Field(None, description="home, work, other (Phase 3)")
    
    # Context
    time_of_day: str = Field(..., description="morning, afternoon, evening, night")
    day_of_week: str
    is_weekend: bool
    hour: int
    
    # Action tracking
    action: str = Field(..., description="weather_check, location_search")
    method: str = Field(..., description="auto_location, manual_search")
    
    # Weather snapshot (for correlation)
    weather_snapshot: Optional[dict] = None


class FashionFeedback(BaseModel):
    """Fashion tip feedback for personalization (Phase 3: ML training)."""
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    weather_conditions: dict
    tips_shown: list
    feedback: str = Field(..., description="helpful, not_helpful, ignored")
    outfit_selected: Optional[str] = None
    notes: Optional[str] = None


class CoordsWeatherRequest(BaseModel):
    """Weather request by coordinates (for 'Use My Location' feature)."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    user_id: Optional[str] = None

class FashionRequest(BaseModel):
    """Request for fashion recommendations."""
    temperature: float = Field(..., description="Temperature in Celsius")
    precipitation: float = Field(0, description="Precipitation in mm")
    wind_speed: float = Field(0, description="Wind speed in km/h")
    uv_index: float = Field(0, description="UV index (0-11+)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 18.5,
                "precipitation": 0.0,
                "wind_speed": 11.2,
                "uv_index": 3
            }
        }
