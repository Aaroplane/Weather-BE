import httpx
import logging
from typing import Optional
from app.models.schemas import Coordinates , LocationOption
from app.config import get_settings


# Module logger
logger = logging.getLogger(__name__)


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

# Disambiguation Function 
async def search_locations(
    query: str, 
    limit: int = 5,
    filter_by_confidence: bool = True 
) -> list[LocationOption]:
    from app.models.schemas import LocationOption
    
    settings = get_settings()
    
    # Handle empty query
    if not query or query.strip() == "":
        return []
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.nominatim_base_url}/search",
                params={
                    "q": query,
                    "format": "json",
                    "limit": max(limit, 10), 
                    "addressdetails": 1
                },
                headers={
                    "User-Agent": "WeatherAgentApp/1.0"
                },
                timeout=10.0
            )
            response.raise_for_status()
            
        except httpx.TimeoutException:
            raise GeocodingError(f"Geocoding service timed out for query: {query}")
        except httpx.HTTPError as e:
            raise GeocodingError(f"Geocoding API error: {str(e)}")
    
    data = response.json()
    
    if not data:
        return []
    
    # Transform ALL results into LocationOption objects
    all_options = []
    for result in data:
        short_name = _extract_short_name(result)
        confidence = _determine_confidence(result)
        
        option = LocationOption(
            latitude=float(result["lat"]),
            longitude=float(result["lon"]),
            location_name=result.get("display_name", query),
            short_name=short_name,
            confidence=confidence,
            location_type=result.get("type", "unknown")
        )
        all_options.append(option)
    
    # Deduplicate (remove near-duplicates)
    deduplicated = _deduplicate_locations(all_options)
    
    # Apply smart confidence filtering if enabled
    if filter_by_confidence:
        filtered = _apply_confidence_filter(deduplicated, limit)
        return filtered
    else:
        return deduplicated[:limit]


def _apply_confidence_filter(
    options: list[LocationOption], 
    limit: int
) -> list[LocationOption]:
    
    if not options:
        return []
    
    # Categorize by confidence
    high = [opt for opt in options if opt.confidence == "high"]
    medium = [opt for opt in options if opt.confidence == "medium"]
    low = [opt for opt in options if opt.confidence == "low"]
    
    # Apply filtering logic
    if high:
        # High confidence exists = use ONLY those
        result = high[:limit]
        logger.info(
            f"Confidence filter: Found {len(high)} high-confidence matches, "
            f"returning {len(result)}"
        )
        return result
    
    elif medium:
        # No high, but medium exists = use ONLY those
        result = medium[:limit]
        logger.info(
            f"Confidence filter: No high-confidence, "
            f"found {len(medium)} medium-confidence matches, "
            f"returning {len(result)}"
        )
        return result
    
    else:
        # Only low confidence = return what we have
        result = low[:limit]
        logger.info(
            f"Confidence filter: Only low-confidence matches, "
            f"returning {len(result)}"
        )
        return result

def _deduplicate_locations(options: list[LocationOption]) -> list[LocationOption]:
    """
    Remove duplicate locations that refer to the same place.
    
    Problem:
        Nominatim returns multiple results for "Brooklyn":
        - Brooklyn (neighborhood center): 40.6526, -73.9497
        - Brooklyn (city hall): 40.6782, -73.9442
        - Brooklyn, Kings County: 40.6500, -73.9500
        
        These all refer to THE SAME PLACE but with slight coordinate differences.
    
    Solution:
        1. Group locations within ~5km radius
        2. Keep the best result from each group
        3. Boost confidence if multiple results agree
    
    Args:
        options: List of LocationOption objects (may have duplicates)
    
    Returns:
        Deduplicated list of LocationOption objects
    """
    if len(options) <= 1:
        return options
    
    # Group locations by proximity
    groups = []
    
    for option in options:
        # Try to find existing group this belongs to
        added_to_group = False
        
        for group in groups:
            # Check if this location is close to any in the group
            for existing in group:
                if _are_locations_similar(option, existing):
                    group.append(option)
                    added_to_group = True
                    break
            
            if added_to_group:
                break
        
        # If not added to any group, create new group
        if not added_to_group:
            groups.append([option])
    
    # From each group, select the best representative
    deduplicated = []
    for group in groups:
        best = _select_best_from_group(group)
        deduplicated.append(best)
    
    logger.info(
        f"Deduplication: {len(options)} results → {len(groups)} groups → "
        f"{len(deduplicated)} unique locations"
    )
    
    return deduplicated


def _are_locations_similar(loc1: LocationOption, loc2: LocationOption) -> bool:
    """
    Check if two locations refer to approximately the same place.
    """
    lat_diff = abs(loc1.latitude - loc2.latitude)
    lon_diff = abs(loc1.longitude - loc2.longitude)
    
    distance_km = ((lat_diff * 111) ** 2 + (lon_diff * 85) ** 2) ** 0.5
    
    SIMILARITY_THRESHOLD_KM = 5.0  # 5km radius
    
    is_similar = distance_km < SIMILARITY_THRESHOLD_KM
    
    if is_similar:
        logger.debug(
            f"Similar locations detected ({distance_km:.2f}km apart): "
            f"{loc1.short_name} vs {loc2.short_name}"
        )
    
    return is_similar


def _select_best_from_group(group: list[LocationOption]) -> LocationOption:
    """
    Select the best representative from a group of duplicate locations.
    """
    if len(group) == 1:
        return group[0]
    
    # Define type priority (higher = better)
    type_priority = {
        "city": 100,
        "town": 90,
        "village": 80,
        "neighbourhood": 70,
        "suburb": 60,
        "administrative": 50,
        "county": 40,
        "state": 30,
        "country": 20
    }
    
    # Score each option
    scored = []
    for option in group:
        score = 0
        
        # Type priority
        score += type_priority.get(option.location_type, 0)
        
        # Confidence boost
        if option.confidence == "high":
            score += 50
        elif option.confidence == "medium":
            score += 25
        
        # Prefer shorter names (more concise)
        score -= len(option.location_name) * 0.1
        
        scored.append((score, option))
    
    # Sort by score (highest first)
    scored.sort(key=lambda x: x[0], reverse=True)
    best_option = scored[0][1]
    
    # Boost confidence if multiple results agree on same location
    if len(group) >= 2:
        if best_option.confidence == "medium":
            # Create new option with boosted confidence
            from app.models.schemas import LocationOption
            best_option = LocationOption(
                latitude=best_option.latitude,
                longitude=best_option.longitude,
                location_name=best_option.location_name,
                short_name=best_option.short_name,
                confidence="high",  # ← BOOSTED
                location_type=best_option.location_type
            )
            logger.info(
                f"Confidence boosted to HIGH for {best_option.short_name} "
                f"(multiple results agree)"
            )
    
    return best_option

def _extract_short_name(geocode_result: dict) -> str:
    
    address = geocode_result.get("address", {})
    display = geocode_result.get("display_name", "")
    
    # Try to build: City, State/Country format
    city = (
        address.get("city") or 
        address.get("town") or 
        address.get("village") or
        address.get("hamlet") or
        display.split(",")[0]  # Fallback to first part
    )
    
    # For US locations
    if address.get("country") == "United States":
        state = address.get("state")
        if state:
            # Convert "New York" → "NY" if possible
            state_abbrev = _get_state_abbrev(state)
            return f"{city}, {state_abbrev}"
    
    # For international locations
    country = address.get("country", "")
    if country:
        return f"{city}, {country}"
    
    # Fallback: just return display name
    return display


def _get_state_abbrev(state_name: str) -> str:
    states = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
        "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
        "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
        "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
        "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
        "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
        "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
        "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
        "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
        "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
        "Wisconsin": "WI", "Wyoming": "WY"
    }
    return states.get(state_name, state_name)
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

