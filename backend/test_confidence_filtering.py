"""Test confidence-based filtering."""
import asyncio
import httpx


async def test_confidence_filtering():
    print("🧪 Testing Smart Confidence Filtering\n")
    print("=" * 80)
    
    base_url = "http://localhost:8000"
    
    test_cases = [
        {
            "query": "Brooklyn, NY",
            "expected": "Should return ONLY high-confidence Brooklyn, NY (no disambiguation)",
            "expect_ambiguous": False
        },
        {
            "query": "Brooklyn",
            "expected": "Should return multiple medium-confidence Brooklyns",
            "expect_ambiguous": True
        },
        {
            "query": "Paris",
            "expected": "Should return Paris, France (high) OR multiple medium if no high",
            "expect_ambiguous": None  # Depends on Nominatim's response
        },
        {
            "query": "Springfield",
            "expected": "Should return top medium-confidence Springfields (many exist)",
            "expect_ambiguous": True
        },
        {
            "query": "Empire State Building",
            "expected": "Should return single high-confidence result",
            "expect_ambiguous": False
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for i, test in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test['query']}")
            print("-" * 80)
            print(f"Expected: {test['expected']}")
            print()
            
            response = await client.post(
                f"{base_url}/api/location/disambiguate",
                json={"location": test["query"]},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"Is Ambiguous: {data['is_ambiguous']}")
                print(f"Matches Returned: {len(data['matches'])}")
                print()
                
                # Show all matches with confidence
                for j, match in enumerate(data['matches'], 1):
                    print(f"  {j}. {match['short_name']}")
                    print(f"     Confidence: {match['confidence']} ← Notice filtering")
                    print(f"     Type: {match['location_type']}")
                
                # Verify expectation
                if test['expect_ambiguous'] is not None:
                    if data['is_ambiguous'] == test['expect_ambiguous']:
                        print(f"\n✅ Result matches expectation!")
                    else:
                        print(f"\n⚠️  Expected ambiguous={test['expect_ambiguous']}, got {data['is_ambiguous']}")
                
                # Show confidence distribution
                confidence_counts = {}
                for match in data['matches']:
                    conf = match['confidence']
                    confidence_counts[conf] = confidence_counts.get(conf, 0) + 1
                
                print(f"\nConfidence Distribution: {confidence_counts}")
                
            else:
                print(f"❌ Error: {response.status_code}")
            
            print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_confidence_filtering())