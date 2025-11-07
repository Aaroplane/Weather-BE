import httpx
from typing import Optional
from app.models.schemas import Coordinates
from app.config import get_settings


class GeocodingError(Exception):
    """Raised when geocoding fails."""
    pass


async def geocode(location: Optional[str]) -> Coordinates:
  
    settings = get_settings()
    
    # Handle null input - use default test location
    if not location or location.strip() == "":
        return Coordinates(
            latitude=settings.default_location_lat,
            longitude=settings.default_location_lon,
            location_name=settings.default_location_name,
            confidence="high"
        )
    
    # Call Nominatim API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.nominatim_base_url}/search",
                params={
                    "q": location,           
                    "format": "json",        
                    "limit": 1,             
                    "addressdetails": 1      
                },
                headers={
                    "User-Agent": "WeatherAgentApp/1.0"  
                },
                timeout=10.0
            )
            response.raise_for_status()
            
        except httpx.TimeoutException:
            raise GeocodingError(f"Geocoding service timed out for location: {location}")
        except httpx.HTTPError as e:
            raise GeocodingError(f"Geocoding API error: {str(e)}")
    
    data = response.json()
    
    if not data or len(data) == 0:
        raise GeocodingError(f"Location not found: {location}")
    
    result = data[0]
    
    # Determine confidence based on result type
    confidence = _determine_confidence(result)
    
    return Coordinates(
        latitude=float(result["lat"]),
        longitude=float(result["lon"]),
        location_name=result.get("display_name", location),
        confidence=confidence
    )


def _determine_confidence(geocode_result: dict) -> str:

    result_type = geocode_result.get("type", "")
    osm_type = geocode_result.get("osm_type", "")
    
    # High confidence: specific buildings, addresses
    if result_type in ["building", "house", "residential"] or osm_type == "way":
        return "high"
    
    # Medium confidence: cities, neighborhoods
    elif result_type in ["city", "town", "village", "neighbourhood"]:
        return "medium"
    
    # Low confidence: broad regions, ambiguous
    else:
        return "low"

