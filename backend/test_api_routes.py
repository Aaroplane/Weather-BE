import asyncio
import httpx


async def test_routes():
    print("🧪 Testing API Routes\n")
    
    # Base URL (assumes uvicorn is running)
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Health check
        print("=" * 60)
        print("Test 1: Health Check")
        print("=" * 60)
        
        response = await client.get(f"{base_url}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test 2: Current weather (with location)
        print("\n" + "=" * 60)
        print("Test 2: Current Weather (Brooklyn, NY)")
        print("=" * 60)
        
        response = await client.post(
            f"{base_url}/api/weather/current",
            json={"location": "Brooklyn, NY"}
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Query: {data['query']}")
        print(f"Location: {data['location']['location_name']}")
        print(f"Temperature: {data['current_weather']['temperature']}°C")
        print(f"Suggestions: {len(data['suggestions'])}")
        for sug in data['suggestions']:
            print(f"  - [{sug['severity']}] {sug['suggestion']}")
        
        # Test 3: Current weather (null location - uses default)
        print("\n" + "=" * 60)
        print("Test 3: Current Weather (null - uses default)")
        print("=" * 60)
        
        response = await client.post(
            f"{base_url}/api/weather/current",
            json={"location": None}
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Used default: {data['location']['location_name']}")
        print(f"Temperature: {data['current_weather']['temperature']}°C")
        
        # Test 4: Invalid location
        print("\n" + "=" * 60)
        print("Test 4: Invalid Location (should return 400)")
        print("=" * 60)
        
        response = await client.post(
            f"{base_url}/api/weather/current",
            json={"location": "xyzinvalidlocation12345"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 400:
            print(f"✅ Expected error: {response.json()['detail']}")


if __name__ == "__main__":
    print("\n⚠️  Make sure uvicorn is running first!")
    print("    Run in another terminal: uvicorn app.main:app --reload\n")
    
    asyncio.run(test_routes())