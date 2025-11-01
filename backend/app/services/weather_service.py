import httpx
from datetime import datetime
from typing import Optional
from app.models.schemas import CurrentWeather, WeatherSuggestion, WeatherResponse, Coordinates
from app.config import get_settings


class WeatherAPIError(Exception):
    """Raised when weather API fails."""
    pass


async def fetch_current_weather(latitude: float, longitude: float) -> CurrentWeather:

    settings = get_settings()
    
    # Define which weather parameters we want from the API
    # These map to your priority ranking: temp > wind > precipitation > humidity > UV
    current_params = [
        "temperature_2m",           # Temperature at 2 meters above ground (°C)
        "precipitation",            # Current precipitation (mm)
        "wind_speed_10m",          # Wind speed at 10 meters (km/h)
        "relative_humidity_2m",    # Relative humidity (%)
        "uv_index"                 # UV index (0-11+)
    ]
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.open_meteo_base_url}/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": ",".join(current_params),  # Join as comma-separated string
                    "temperature_unit": "celsius",        # Use metric
                    "wind_speed_unit": "kmh",
                    "precipitation_unit": "mm"
                },
                timeout=15.0  # Open-Meteo is usually fast, but allow 15s
            )
            response.raise_for_status()
            
        except httpx.TimeoutException:
            raise WeatherAPIError(f"Weather API timed out for coordinates ({latitude}, {longitude})")
        except httpx.HTTPError as e:
            raise WeatherAPIError(f"Weather API error: {str(e)}")
    
    # Parse API response
    data = response.json()
    
    if "current" not in data:
        raise WeatherAPIError("Invalid response from weather API: missing 'current' data")
    
    current = data["current"]
    
    # Transform Open-Meteo response → Our CurrentWeather schema
    # Note: Open-Meteo doesn't always provide UV index, so we default to 0.0
    return CurrentWeather(
        timestamp=datetime.fromisoformat(current["time"]),
        temperature=float(current.get("temperature_2m", 0.0)),
        precipitation=float(current.get("precipitation", 0.0)),
        wind_speed=float(current.get("wind_speed_10m", 0.0)),
        humidity=float(current.get("relative_humidity_2m", 0.0)),
        uv_index=float(current.get("uv_index", 0.0))
    )


def generate_suggestions(weather: CurrentWeather) -> list[WeatherSuggestion]:
    """
    Apply rule-based logic to generate weather suggestions.
    
    This implements your priority ranking:
        1. Temperature (most important)
        2. Wind conditions
        3. Precipitation
        4. Humidity
        5. UV index (least important)
    
    Args:
        weather: Current weather conditions
    
    Returns:
        List of suggestions (can be empty if conditions are normal)
    
    Why separate function:
        - Keeps business logic separate from API calls
        - Easy to test without hitting external APIs
        - Can be enhanced with ML models later (Phase 4)
    """
    suggestions = []
    
    # RULE 1: Temperature (Priority #1)
    if weather.temperature < 0:
        suggestions.append(WeatherSuggestion(
            rule_triggered="extreme_cold",
            severity="high",
            suggestion="⚠️ Freezing conditions! Dress in layers, cover exposed skin. Limit outdoor time.",
            icon="🥶"
        ))
    elif weather.temperature < 10:
        suggestions.append(WeatherSuggestion(
            rule_triggered="cold_weather",
            severity="moderate",
            suggestion="🧥 Cold weather. Wear a jacket and consider gloves.",
            icon="🧥"
        ))
    elif weather.temperature > 35:
        suggestions.append(WeatherSuggestion(
            rule_triggered="extreme_heat",
            severity="high",
            suggestion="🌡️ Extreme heat! Stay hydrated, seek shade, avoid strenuous outdoor activities.",
            icon="🔥"
        ))
    elif weather.temperature > 30:
        suggestions.append(WeatherSuggestion(
            rule_triggered="hot_weather",
            severity="moderate",
            suggestion="☀️ Hot weather. Wear light clothing, drink plenty of water.",
            icon="☀️"
        ))
    elif 15 <= weather.temperature <= 25:
        suggestions.append(WeatherSuggestion(
            rule_triggered="optimal_temperature",
            severity="low",
            suggestion="✨ Perfect temperature for outdoor activities!",
            icon="😊"
        ))
    
    # RULE 2: Wind (Priority #2)
    if weather.wind_speed > 50:
        suggestions.append(WeatherSuggestion(
            rule_triggered="dangerous_wind",
            severity="high",
            suggestion="💨 Dangerous wind conditions! Stay indoors. Secure loose objects.",
            icon="🌪️"
        ))
    elif weather.wind_speed > 30:
        suggestions.append(WeatherSuggestion(
            rule_triggered="high_wind",
            severity="moderate",
            suggestion="🌬️ Windy conditions. Difficult for outdoor activities. Watch for debris.",
            icon="💨"
        ))
    
    # RULE 3: Precipitation (Priority #3)
    if weather.precipitation > 10:
        suggestions.append(WeatherSuggestion(
            rule_triggered="heavy_rain",
            severity="high",
            suggestion="⛈️ Heavy rain! Avoid travel if possible. Roads may flood.",
            icon="⛈️"
        ))
    elif weather.precipitation > 2:
        suggestions.append(WeatherSuggestion(
            rule_triggered="moderate_rain",
            severity="moderate",
            suggestion="🌧️ Rainy weather. Bring an umbrella, drive carefully.",
            icon="☔"
        ))
    elif weather.precipitation > 0:
        suggestions.append(WeatherSuggestion(
            rule_triggered="light_rain",
            severity="low",
            suggestion="🌦️ Light rain. You might want an umbrella.",
            icon="🌦️"
        ))
    
    # RULE 4: Humidity (Priority #4)
    if weather.humidity > 80 and weather.temperature > 25:
        suggestions.append(WeatherSuggestion(
            rule_triggered="high_humidity",
            severity="moderate",
            suggestion="💧 High humidity makes it feel warmer. Pace yourself, stay hydrated.",
            icon="💧"
        ))
    
    # RULE 5: UV Index (Priority #5)
    if weather.uv_index >= 8:
        suggestions.append(WeatherSuggestion(
            rule_triggered="high_uv",
            severity="moderate",
            suggestion="☀️ High UV index. Wear sunscreen (SPF 30+), sunglasses, and a hat.",
            icon="🕶️"
        ))
    
    # If no rules triggered, provide positive message
    if not suggestions:
        suggestions.append(WeatherSuggestion(
            rule_triggered="normal_conditions",
            severity="low",
            suggestion="🌤️ Weather conditions are pleasant. Great day to be outside!",
            icon="👍"
        ))
    
    return suggestions


async def get_weather_with_suggestions(
    latitude: float,
    longitude: float,
    location: Coordinates
) -> WeatherResponse:
    """
    Complete workflow: Fetch weather + generate suggestions.
    
    This is the HIGH-LEVEL function that routes will call.
    It orchestrates the complete weather retrieval process.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        location: Coordinates object (includes resolved location name)
    
    Returns:
        Complete WeatherResponse with location, weather, and suggestions
    
    Integration Point:
        This will be called by routes.py like:
        
        coords = await geocoding_service.geocode("Brooklyn")
        response = await weather_service.get_weather_with_suggestions(
            coords.latitude,
            coords.longitude,
            coords
        )
    """
    # Step 1: Fetch current weather from API
    weather = await fetch_current_weather(latitude, longitude)
    
    # Step 2: Apply rule engine to generate suggestions
    suggestions = generate_suggestions(weather)
    
    # Step 3: Package everything into response schema
    return WeatherResponse(
        query=location.location_name,  # What was searched
        location=location,              # Resolved coordinates
        current_weather=weather,        # Weather data
        suggestions=suggestions,        # AI suggestions
        timestamp=datetime.now()        # When this response was generated
    )


# ============================================================================
# WHY THIS STRUCTURE?
# ============================================================================
#
# 1. SEPARATION OF CONCERNS:
#    - fetch_current_weather() = Pure API call (no business logic)
#    - generate_suggestions() = Pure business logic (no API calls)
#    - get_weather_with_suggestions() = Orchestration (combines both)
#    
#    Why? Each function is independently testable and reusable
#
# 2. PRIORITY-BASED RULES:
#    - Rules are checked in order of your importance ranking
#    - Most critical warnings (temp, wind) checked first
#    - Less critical (humidity, UV) checked last
#    - Severity levels help frontend prioritize display
#
# 3. SCHEMA VALIDATION:
#    - CurrentWeather schema ensures API data is valid
#    - WeatherResponse schema ensures complete, consistent output
#    - Pydantic catches issues before they reach the user
#
# 4. ERROR HANDLING:
#    - Custom WeatherAPIError makes debugging clear
#    - Routes can catch this and return helpful error messages
#    - Better than generic exceptions
#
# 5. ASYNC ALL THE WAY:
#    - All I/O operations are async (API calls)
#    - Python can handle multiple requests concurrently
#    - Critical for performance under load
#
# ============================================================================