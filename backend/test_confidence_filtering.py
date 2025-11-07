"""Test confidence-based filtering with deduplication."""
import asyncio
import httpx


async def test_deduplication():
    print("🧪 Testing Deduplication + Smart Confidence Filtering\n")
    print("=" * 80)
    
    base_url = "http://localhost:8000"
    
    test_cases = [
        {
            "query": "Brooklyn",
            "description": "Should dedupe multiple Brooklyn entries, boost confidence",
            "expect_duplicates": False
        },
        {
            "query": "Brooklyn, NY",
            "description": "Specific query - should return 1 high-confidence result",
            "expect_ambiguous": False
        },
        {
            "query": "Paris",
            "description": "Multiple distinct cities - should NOT dedupe",
            "expect_ambiguous": True
        },
        {
            "query": "Springfield",
            "description": "Many distinct cities - should keep separate",
            "expect_ambiguous": True
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for i, test in enumerate(test_cases, 1):
            print(f"\nTest {i}: '{test['query']}'")
            print("-" * 80)
            print(f"Description: {test['description']}")
            print()
            
            try:
                response = await client.post(
                    f"{base_url}/api/location/disambiguate",
                    json={"location": test["query"]},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    print(f"✅ Status: {response.status_code}")
                    print(f"Is Ambiguous: {data['is_ambiguous']}")
                    print(f"Unique Locations: {len(data['matches'])}")
                    print()
                    
                    # Check for duplicates (same short_name)
                    short_names = [m['short_name'] for m in data['matches']]
                    unique_names = set(short_names)
                    has_duplicates = len(short_names) != len(unique_names)
                    
                    if has_duplicates:
                        print("⚠️  WARNING: Duplicate short names detected!")
                        from collections import Counter
                        dupes = Counter(short_names)
                        for name, count in dupes.items():
                            if count > 1:
                                print(f"   '{name}' appears {count} times")
                    else:
                        print("✅ No duplicate short names (deduplication working)")
                    
                    print()
                    
                    # Show all matches
                    for j, match in enumerate(data['matches'], 1):
                        print(f"  {j}. {match['short_name']}")
                        print(f"     Coordinates: ({match['latitude']:.4f}, {match['longitude']:.4f})")
                        print(f"     Confidence: {match['confidence']}")
                        print(f"     Type: {match['location_type']}")
                    
                    # Check expectations
                    if 'expect_ambiguous' in test:
                        if data['is_ambiguous'] == test['expect_ambiguous']:
                            print(f"\n✅ Ambiguity matches expectation ({test['expect_ambiguous']})")
                        else:
                            print(f"\n⚠️  Expected ambiguous={test['expect_ambiguous']}, got {data['is_ambiguous']}")
                    
                    if 'expect_duplicates' in test:
                        if has_duplicates == test['expect_duplicates']:
                            print(f"✅ Duplicate check matches expectation ({test['expect_duplicates']})")
                        else:
                            print(f"⚠️  Expected duplicates={test['expect_duplicates']}, got {has_duplicates}")
                    
                    # Show confidence distribution
                    confidence_counts = {}
                    for match in data['matches']:
                        conf = match['confidence']
                        confidence_counts[conf] = confidence_counts.get(conf, 0) + 1
                    
                    print(f"\nConfidence Distribution: {confidence_counts}")
                    
                else:
                    print(f"❌ Error: Status {response.status_code}")
                    print(f"   Detail: {response.json().get('detail', 'Unknown')}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
            
            print("\n" + "=" * 80)


async def test_coordinate_variations():
    """Test that locations with slight coordinate differences are deduped."""
    print("\n\n🔬 Testing Coordinate Deduplication\n")
    print("=" * 80)
    
    base_url = "http://localhost:8000"
    
    query = "Brooklyn, New York"
    
    print(f"Query: '{query}'")
    print("Expected: Should collapse multiple Brooklyn coordinate variations into 1 result")
    print()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/api/location/disambiguate",
            json={"location": query},
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"Results: {len(data['matches'])} location(s)")
            print()
            
            # Show coordinate variations
            for i, match in enumerate(data['matches'], 1):
                print(f"{i}. {match['short_name']}")
                print(f"   Lat/Lon: ({match['latitude']:.6f}, {match['longitude']:.6f})")
                print(f"   Confidence: {match['confidence']}")
                print()
            
            if len(data['matches']) == 1:
                print("✅ SUCCESS: Multiple coordinate variations collapsed into 1 result!")
                if data['matches'][0]['confidence'] == 'high':
                    print("✅ BONUS: Confidence boosted to HIGH (multiple results agreed)")
            elif len(data['matches']) > 1:
                # Check if they're actually different places
                coords = [(m['latitude'], m['longitude']) for m in data['matches']]
                # Calculate distances
                print("⚠️  Multiple results remain. Checking distances...")
                for i in range(len(coords)):
                    for j in range(i+1, len(coords)):
                        lat_diff = abs(coords[i][0] - coords[j][0])
                        lon_diff = abs(coords[i][1] - coords[j][1])
                        distance_km = ((lat_diff * 111) ** 2 + (lon_diff * 85) ** 2) ** 0.5
                        print(f"   Distance between result {i+1} and {j+1}: {distance_km:.2f}km")


if __name__ == "__main__":
    print("\n⚠️  PREREQUISITES:")
    print("   Make sure uvicorn is running on http://localhost:8000")
    print("\nStarting tests in 2 seconds...\n")
    
    import time
    time.sleep(2)
    
    asyncio.run(test_deduplication())
    asyncio.run(test_coordinate_variations())