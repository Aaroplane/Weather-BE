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
    current_params = [
        "temperature_2m",          
        "precipitation",           
        "relative_humidity_2m",   
        "uv_index"                 
    ]
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.open_meteo_base_url}/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": ",".join(current_params), 
                    "temperature_unit": "celsius",        # Use metric
                    "wind_speed_unit": "kmh",
                    "precipitation_unit": "mm"
                },
                timeout=15.0  
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
    

    return CurrentWeather(
        timestamp=datetime.fromisoformat(current["time"]),
        temperature=float(current.get("temperature_2m", 0.0)),
        precipitation=float(current.get("precipitation", 0.0)),
        wind_speed=float(current.get("wind_speed_10m", 0.0)),
        humidity=float(current.get("relative_humidity_2m", 0.0)),
        uv_index=float(current.get("uv_index", 0.0))
    )


def generate_suggestions(weather: CurrentWeather) -> list[WeatherSuggestion]:
   
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
    
    weather = await fetch_current_weather(latitude, longitude)
    
    suggestions = generate_suggestions(weather)
    
    return WeatherResponse(
        query=location.location_name,  
        location=location,              
        current_weather=weather,        
        suggestions=suggestions,
        timestamp=datetime.now()        
    )


