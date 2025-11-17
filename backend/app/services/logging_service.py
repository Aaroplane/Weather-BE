import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from app.models.schemas import UserPreference, LocationLog, FashionFeedback

logger = logging.getLogger(__name__)

DATA_DIR = Path("data/logs")
DATA_DIR.mkdir(parents=True, exist_ok=True)

class LoggingService:
    """Service for logging user interactions for future RAG/ML."""
    
    @staticmethod
    async def log_preference(preference: UserPreference) -> None:
        """Log user preference."""
        try:
            file_path = DATA_DIR / f"preferences_{preference.user_id}.jsonl"
            
            with open(file_path, "a") as f:
                f.write(json.dumps(preference.dict(), default=str) + "\n")
            
            logger.info(f"✅ Logged preference: {preference.preference_type} = {preference.value}")
        except Exception as e:
            logger.error(f"❌ Failed to log preference: {e}")
    
    
    @staticmethod
    async def log_location(log: LocationLog) -> None:
        """Log location access for pattern detection."""
        try:
            file_path = DATA_DIR / f"locations_{log.user_id}.jsonl"
            
            with open(file_path, "a") as f:
                f.write(json.dumps(log.dict(), default=str) + "\n")
            
            logger.info(f"✅ Logged location: {log.location_name} at {log.time_of_day}")
        except Exception as e:
            logger.error(f"❌ Failed to log location: {e}")
    
    
    @staticmethod
    async def log_fashion_feedback(feedback: FashionFeedback) -> None:
        """Log fashion tip feedback."""
        try:
            file_path = DATA_DIR / f"fashion_{feedback.user_id}.jsonl"
            
            with open(file_path, "a") as f:
                f.write(json.dumps(feedback.dict(), default=str) + "\n")
            
            logger.info(f"✅ Logged fashion feedback: {feedback.feedback}")
        except Exception as e:
            logger.error(f"❌ Failed to log feedback: {e}")
    
    
    @staticmethod
    async def get_user_preferences(user_id: str) -> Dict[str, Any]:
        """Retrieve user preferences."""
        try:
            file_path = DATA_DIR / f"preferences_{user_id}.jsonl"
            
            if not file_path.exists():
                return {}
            
            preferences = {}
            with open(file_path, "r") as f:
                for line in f:
                    pref = json.loads(line)
                    preferences[pref["preference_type"]] = pref["value"]
            
            return preferences
        except Exception as e:
            logger.error(f"❌ Failed to retrieve preferences: {e}")
            return {}
    
    
    @staticmethod
    async def get_recent_locations(user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent location searches."""
        try:
            file_path = DATA_DIR / f"locations_{user_id}.jsonl"
            
            if not file_path.exists():
                return []
            
            locations = []
            with open(file_path, "r") as f:
                for line in f:
                    locations.append(json.loads(line))
            
            # Return most recent first
            return locations[-limit:][::-1]
        except Exception as e:
            logger.error(f"❌ Failed to retrieve locations: {e}")
            return []


logging_service = LoggingService()