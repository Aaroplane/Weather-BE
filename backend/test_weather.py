"""Test weather service in isolation."""
import asyncio
from app.services.weather_service import (
    fetch_current_weather,
    generate_suggestions,
    get_weather_with_suggestions,
    WeatherAPIError
)
from app.models.schemas import Coordinates


async def test_weather_service():
    print("🧪 Testing Weather Service\n")
    print("=" * 60)
    
    # Test coordinates (Brooklyn, NY)
    test_lat = 40.6782
    test_lon = -73.9442
    
    # Test 1: Fetch current weather
    print(f"Test 1: Fetch weather for coordinates ({test_lat}, {test_lon})")
    try:
        weather = await fetch_current_weather(test_lat, test_lon)
        print(f"✅ Success!")
        print(f"   Temperature: {weather.temperature}°C")
        print(f"   Wind Speed: {weather.wind_speed} km/h")
        print(f"   Precipitation: {weather.precipitation} mm")
        print(f"   Humidity: {weather.humidity}%")
        print(f"   UV Index: {weather.uv_index}")
        print(f"   Timestamp: {weather.timestamp}")
    except WeatherAPIError as e:
        print(f"❌ Failed: {e}")
        return
    
    print("\n" + "=" * 60)
    
    # Test 2: Generate suggestions based on weather
    print("Test 2: Generate suggestions for current weather")
    suggestions = generate_suggestions(weather)
    print(f"✅ Generated {len(suggestions)} suggestion(s):")
    for i, sug in enumerate(suggestions, 1):
        print(f"   {i}. [{sug.severity.upper()}] {sug.suggestion}")
        print(f"      Rule: {sug.rule_triggered}")
    
    print("\n" + "=" * 60)
    
    # Test 3: Complete workflow
    print("Test 3: Complete workflow (weather + suggestions)")
    coords = Coordinates(
        latitude=test_lat,
        longitude=test_lon,
        location_name="Brooklyn, NY (Test)",
        confidence="high"
    )
    
    try:
        response = await get_weather_with_suggestions(
            test_lat,
            test_lon,
            coords
        )
        print(f"✅ Success!")
        print(f"   Query: {response.query}")
        print(f"   Location: {response.location.location_name}")
        print(f"   Temperature: {response.current_weather.temperature}°C")
        print(f"   Suggestions: {len(response.suggestions)}")
    except WeatherAPIError as e:
        print(f"❌ Failed: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 4: Test extreme conditions (mock data)
    print("Test 4: Test rule engine with extreme conditions")
    from app.models.schemas import CurrentWeather
    from datetime import datetime
    
    extreme_weather = CurrentWeather(
        timestamp=datetime.now(),
        temperature=38.0,    # Extreme heat
        precipitation=15.0,  # Heavy rain
        wind_speed=55.0,     # Dangerous wind
        humidity=85.0,       # High humidity
        uv_index=10.0        # High UV
    )
    
    extreme_suggestions = generate_suggestions(extreme_weather)
    print(f"✅ Generated {len(extreme_suggestions)} warnings for extreme conditions:")
    for sug in extreme_suggestions:
        print(f"   🚨 [{sug.severity.upper()}] {sug.icon} {sug.suggestion}")
    
    print("\n" + "=" * 60)
    print("🎉 Weather service tests complete!")


if __name__ == "__main__":
    asyncio.run(test_weather_service())