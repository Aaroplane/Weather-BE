from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App Settings
    app_name: str = "Weather Agent API"
    debug: bool = True
    environment: str = "development"
    
    # fallback when user input is null
    default_location_name: str = "New York, NY"
    default_location_lat: float = 40.7128
    default_location_lon: float = -74.0060
    
    # External APIs
    open_meteo_base_url: str = "https://api.open-meteo.com/v1"
    nominatim_base_url: str = "https://nominatim.openstreetmap.org"
    
    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()