import asyncio
import httpx


async def test_disambiguation():
    print("🧪 Testing Location Disambiguation\n")
    
    base_url = "http://localhost:8000"
    
    test_cases = [
        {
            "query": "Paris",
            "description": "Very ambiguous - multiple famous cities"
        },
        {
            "query": "Springfield",
            "description": "Extremely ambiguous - 33+ US cities"
        },
        {
            "query": "Brooklyn",
            "description": "Moderately ambiguous - several states"
        },
        {
            "query": "Brooklyn, NY",
            "description": "Specific - should have 1-2 matches"
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for test in test_cases:
            print("=" * 80)
            print(f"Query: '{test['query']}'")
            print(f"Description: {test['description']}")
            print("-" * 80)
            
            response = await client.post(
                f"{base_url}/api/location/disambiguate",
                json={"location": test["query"]},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"Is Ambiguous: {data['is_ambiguous']}")
                print(f"Found {len(data['matches'])} matches:\n")
                
                for i, match in enumerate(data['matches'][:5], 1):
                    print(f"  {i}. {match['short_name']}")
                    print(f"     Full: {match['location_name'][:60]}...")
                    print(f"     Confidence: {match['confidence']}")
                    print(f"     Type: {match['location_type']}")
                    print()
            else:
                print(f"❌ Error: {response.status_code}")
            
            print()


if __name__ == "__main__":
    asyncio.run(test_disambiguation())