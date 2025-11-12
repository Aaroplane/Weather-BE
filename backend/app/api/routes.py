from fastapi import APIRouter, HTTPException, status
from app.models.schemas import LocationInput, WeatherResponse, LocationDisambiguationResponse
from app.services import geocoding_service, weather_service
from app.services.geocoding_service import GeocodingError
from app.services.weather_service import WeatherAPIError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["weather"]
)

@router.get("/health")
async def health_check():
    """Health check endpoint."""

    return {
        "status": "healthy",
        "service": "Weather Agent API",
        "version": "1.0.0"
    }

@router.post("/weather/current", response_model=WeatherResponse)
async def get_current_weather(location_input: LocationInput):
    try:
        # Converts "Brooklyn, NY" → Coordinates(lat, lon)
        logger.info(f"Geocoding location: {location_input.location}")
        
        coords = await geocoding_service.geocode(location_input.location)
        
        logger.info(
            f"Geocoded to: {coords.location_name} "
            f"({coords.latitude}, {coords.longitude})"
        )
        
    except GeocodingError as e:
        # User provided invalid/unfindable location
        logger.error(f"Geocoding failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not find location: {str(e)}"
        )
    try:
        logger.info(
            f"Fetching weather for ({coords.latitude}, {coords.longitude})"
        )
        
        response = await weather_service.get_weather_with_suggestions(
            coords.latitude,
            coords.longitude,
            coords
        )
        
        logger.info(
            f"Weather fetched: {response.current_weather.temperature}°C, "
            f"{len(response.suggestions)} suggestion(s)"
        )
        
        return response
    
    except WeatherAPIError as e:
        # External weather API failed
        logger.error(f"Weather API failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Weather service temporarily unavailable: {str(e)}"
        )
    
    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )
    
@router.post("/location/disambiguate", response_model=LocationDisambiguationResponse)
async def disambiguate_location(location_input: LocationInput):

    from app.models.schemas import LocationDisambiguationResponse
    
    try:
        logger.info(f"Searching for locations matching: {location_input.location}")
        
        # Search with smart confidence filtering enabled
        matches = await geocoding_service.search_locations(
            location_input.location or "",
            limit=5,
            filter_by_confidence=True  
        )
        
        # Determine if ambiguous
        is_ambiguous = len(matches) > 1
        
        logger.info(
            f"Found {len(matches)} filtered matches, "
            f"ambiguous={is_ambiguous}"
        )
        
        return LocationDisambiguationResponse(
            query=location_input.location or "",
            matches=matches,
            is_ambiguous=is_ambiguous
        )
        
    except GeocodingError as e:
        logger.error(f"Geocoding failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not search for location: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while searching locations."
        )