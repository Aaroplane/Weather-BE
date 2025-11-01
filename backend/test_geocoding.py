"""Test geocoding service in isolation."""
import asyncio
from app.services.geocoding_service import geocode, GeocodingError


async def test_geocoding():
    print("🧪 Testing Geocoding Service\n")
    print("=" * 60)
    
    # Test 1: Valid location
    print("Test 1: Valid location (Brooklyn, NY)")
    try:
        coords = await geocode("Brooklyn, NY")
        print(f"✅ Success!")
        print(f"   Latitude: {coords.latitude}")
        print(f"   Longitude: {coords.longitude}")
        print(f"   Name: {coords.location_name}")
        print(f"   Confidence: {coords.confidence}")
    except GeocodingError as e:
        print(f"❌ Failed: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Null input (should use default)
    print("Test 2: Null input (should use default from .env)")
    try:
        coords = await geocode(None)
        print(f"✅ Success!")
        print(f"   Used default: {coords.location_name}")
        print(f"   Coordinates: ({coords.latitude}, {coords.longitude})")
    except GeocodingError as e:
        print(f"❌ Failed: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 3: Ambiguous location
    print("Test 3: Ambiguous location (Paris)")
    try:
        coords = await geocode("Paris")
        print(f"✅ Success!")
        print(f"   Found: {coords.location_name}")
        print(f"   Confidence: {coords.confidence}")
        print(f"   Note: Could be Paris, France or Paris, Texas")
    except GeocodingError as e:
        print(f"❌ Failed: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 4: Invalid location
    print("Test 4: Invalid location (should fail)")
    try:
        coords = await geocode("asdfjkl12345nonexistent")
        print(f"✅ Success: {coords}")
    except GeocodingError as e:
        print(f"✅ Expected failure: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Geocoding tests complete!")


if __name__ == "__main__":
    asyncio.run(test_geocoding())