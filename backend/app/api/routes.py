from fastapi import APIRouter, HTTPException, status
from app.models.schemas import LocationInput, WeatherResponse, LocationDisambiguationResponse
from app.services import geocoding_service, weather_service
from app.services.geocoding_service import GeocodingError
from app.services.weather_service import WeatherAPIError
from app.services.logging_service import logging_service
from app.services.fashion_service import fashion_service
from app.models.schemas import (
    UserPreference, 
    LocationLog, 
    FashionFeedback,
    CoordsWeatherRequest
)
from typing import Dict, Any
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
@router.post("/preferences")
async def save_preference(preference: UserPreference):
    """Save user preference for future personalization (Phase 3: RAG)."""
    await logging_service.log_preference(preference)
    
    return {
        "status": "success",
        "message": "Preference saved",
        "preference": preference.preference_type
    }


@router.get("/preferences/{user_id}")
async def get_preferences(user_id: str):
    """Get user preferences."""
    preferences = await logging_service.get_user_preferences(user_id)
    
    return {
        "user_id": user_id,
        "preferences": preferences
    }


@router.post("/weather/by-coords", response_model=WeatherResponse)
async def get_weather_by_coords(request: CoordsWeatherRequest):
    """
    Get weather by GPS coordinates (for 'Use My Location' feature).
    Also logs location access for pattern detection.
    """
    try:
        # Reverse geocode coordinates to location name
        import httpx
        from app.services.geocoding_service import reverse_geocode
        
        async with httpx.AsyncClient() as session:
            location_name = await reverse_geocode(
                request.latitude, 
                request.longitude, 
                session
            )
        
        if not location_name:
            location_name = f"Location ({request.latitude:.2f}, {request.longitude:.2f})"
        
        # Create Coordinates object
        coords = Coordinates(
            latitude=request.latitude,
            longitude=request.longitude,
            location_name=location_name,
            confidence="high"
        )
        
        # Log location access (RAG prep)
        if request.user_id:
            now = datetime.now()
            hour = now.hour
            
            # Determine time of day
            if 5 <= hour < 12:
                time_of_day = "morning"
            elif 12 <= hour < 17:
                time_of_day = "afternoon"
            elif 17 <= hour < 21:
                time_of_day = "evening"
            else:
                time_of_day = "night"
            
            location_log = LocationLog(
                user_id=request.user_id,
                latitude=request.latitude,
                longitude=request.longitude,
                location_name=location_name,
                time_of_day=time_of_day,
                day_of_week=now.strftime("%A").lower(),
                is_weekend=now.weekday() >= 5,
                hour=hour,
                action="weather_check",
                method="auto_location"
            )
            await logging_service.log_location(location_log)
        
        # Fetch weather (reuse existing service)
        response = await weather_service.get_weather_with_suggestions(
            coords.latitude,
            coords.longitude,
            coords
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in by-coords: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch weather: {str(e)}"
        )


@router.post("/fashion/recommendations")
async def get_fashion_recommendations(weather_data: Dict[str, Any]):
    """
    Get outfit recommendations based on weather.
    
    Request body example:
    {
        "temperature": 18.5,
        "precipitation": 0.0,
        "wind_speed": 11.2,
        "uv_index": 3
    }
    """
    try:
        recommendations = fashion_service.get_recommendations(weather_data)
        
        return {
            "status": "success",
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Fashion recommendations error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations"
        )


@router.post("/feedback/fashion")
async def save_fashion_feedback(feedback: FashionFeedback):
    """Save fashion tip feedback for personalization (Phase 3: ML)."""
    await logging_service.log_fashion_feedback(feedback)
    
    return {
        "status": "success",
        "message": "Feedback saved"
    }


@router.get("/locations/recent/{user_id}")
async def get_recent_locations(user_id: str, limit: int = 10):
    """Get user's recent location searches."""
    locations = await logging_service.get_recent_locations(user_id, limit)
    
    return {
        "user_id": user_id,
        "locations": locations,
        "count": len(locations)
    }