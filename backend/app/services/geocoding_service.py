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
                    "addressdetails": 1,
                    "accept-language": "en"      
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
    """Search for multiple location matches (for disambiguation)."""
    
    from app.models.schemas import LocationOption
    
    settings = get_settings()
    
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
    
    relevant = _filter_relevant_results(all_options, query)
    
    deduplicated = _deduplicate_locations(relevant)
    
    if filter_by_confidence:
        filtered = _apply_confidence_filter(deduplicated, limit)
        return filtered
    else:
        return deduplicated[:limit]

def _filter_relevant_results(
    options: list[LocationOption],
    original_query: str
) -> list[LocationOption]:
   
    if not options or not original_query:
        return options
    
    query_lower = original_query.lower().strip()
    query_words = set(query_lower.split())
    
    filtered = []
    
    for option in options:
        # Extract searchable text from location
        searchable_text = f"{option.short_name} {option.location_name}".lower()
        location_words = set(searchable_text.split())
        
        has_match = bool(query_words & location_words)
        
        is_substring = query_lower in searchable_text
        
        if has_match or is_substring:
            filtered.append(option)
            logger.debug(f"Relevant: {option.short_name} (matches query '{original_query}')")
        else:
            logger.debug(f"Filtered out: {option.short_name} (doesn't match query '{original_query}')")
    
    logger.info(
        f"Relevance filter: {len(options)} results → {len(filtered)} relevant "
        f"(removed {len(options) - len(filtered)} irrelevant)"
    )
    
    return filtered

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

    if len(options) <= 1:
        return options
    
    # Group locations by proximity
    groups = []
    
    for option in options:
        added_to_group = False
        
        for group in groups:
            for existing in group:
                if _are_locations_similar(option, existing):
                    group.append(option)
                    added_to_group = True
                    break
            
            if added_to_group:
                break
        
        if not added_to_group:
            groups.append([option])
    
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
    
    scored = []
    for option in group:
        score = 0
        
        score += type_priority.get(option.location_type, 0)
        
        if option.confidence == "high":
            score += 50
        elif option.confidence == "medium":
            score += 25
        
        score -= len(option.location_name) * 0.1
        
        scored.append((score, option))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    best_option = scored[0][1]
    
    if len(group) >= 2:
        if best_option.confidence == "medium":
            # Create new option with boosted confidence
            from app.models.schemas import LocationOption
            best_option = LocationOption(
                latitude=best_option.latitude,
                longitude=best_option.longitude,
                location_name=best_option.location_name,
                short_name=best_option.short_name,
                confidence="high", 
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
    
    city = (
        address.get("city") or 
        address.get("town") or 
        address.get("village") or
        address.get("hamlet") or
        display.split(",")[0] or
        address.get("neighbourhood") or 
        address.get("suburb") or         
        address.get("county") or 
        None
    )
    
    if not city:
        parts = [p.strip() for p in display.split(",")]
        city = parts[0] if parts else "Unknown"
    
    if city and city.startswith("City of "):
        city = city.replace("City of ", "")
    
    country = address.get("country", "")
    if country in ["United States", "United States of America", "USA"]:
        state = address.get("state")
        
        if state:
            state_abbrev = _get_state_abbrev(state)
            return f"{city}, {state_abbrev}"
        else:
            return f"{city}, USA"
    
    if country and country != "United States":
        return f"{city}, {country}"
    
    parts = [p.strip() for p in display.split(",")]
    if len(parts) >= 2:
        return f"{parts[0]}, {parts[1]}"
    elif len(parts) == 1:
        return parts[0]
    else:
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
    """
    Determine how confident we are in the geocoding result.
     High confidence: specific buildings, addresses, major cities"""
    result_type = geocode_result.get("type", "")
    osm_type = geocode_result.get("osm_type", "")
    importance = geocode_result.get("importance", 0.0)  
    
    if importance >= 0.7:
        return "high"
    
    # High confidence: specific buildings, addresses, major cities
    if result_type in ["city"] and importance >= 0.5:
        return "high"
    
    if result_type in ["building", "house", "residential"] or osm_type == "way":
        return "high"
    
    # Medium confidence: cities, neighborhoods
    if result_type in ["town", "village", "neighbourhood", "suburb"]:
        return "medium"
    
    # Low confidence: broad regions, ambiguous
    return "low"

