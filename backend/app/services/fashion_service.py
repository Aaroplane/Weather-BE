from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class FashionService:
    """Generate outfit recommendations based on weather conditions."""
    
    @staticmethod
    def get_recommendations(weather: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fashion recommendations.
        
        Args:
            weather: Dict with temperature, precipitation, wind_speed, uv_index
            
        Returns:
            Dict with outfit recommendations and tips
        """
        temp = weather.get("temperature", 20)
        precip = weather.get("precipitation", 0)
        wind_speed = weather.get("wind_speed", 0)
        uv_index = weather.get("uv_index", 0)
        
        recommendation = {
            "summary": "",
            "layers": {
                "base": [],
                "mid": [],
                "outer": []
            },
            "accessories": [],
            "footwear": [],
            "tips": []
        }
        
        # Temperature-based clothing
        if temp < 0:
            recommendation["summary"] = "🥶 Bundle up! Freezing conditions."
            recommendation["layers"]["base"] = ["Thermal underwear", "Thick socks"]
            recommendation["layers"]["mid"] = ["Warm sweater", "Fleece layer"]
            recommendation["layers"]["outer"] = ["Heavy winter coat"]
            recommendation["accessories"] = ["Winter hat", "Gloves", "Scarf"]
            recommendation["footwear"] = ["Insulated winter boots"]
            recommendation["tips"] = [
                "Layer up - dress warmer than you think",
                "Cover all exposed skin",
                "Limit outdoor time if possible"
            ]
            
        elif 0 <= temp < 10:
            recommendation["summary"] = "🧥 Cold weather. Dress warmly in layers."
            recommendation["layers"]["base"] = ["Long-sleeve shirt"]
            recommendation["layers"]["mid"] = ["Sweater or hoodie"]
            recommendation["layers"]["outer"] = ["Jacket or coat"]
            recommendation["accessories"] = ["Light scarf", "Gloves (optional)"]
            recommendation["footwear"] = ["Closed-toe shoes", "Boots"]
            recommendation["tips"] = [
                "Layering is key",
                "Bring an extra layer just in case"
            ]
            
        elif 10 <= temp < 18:
            recommendation["summary"] = "😊 Cool and comfortable. Light layers."
            recommendation["layers"]["base"] = ["Long-sleeve shirt or T-shirt"]
            recommendation["layers"]["mid"] = ["Light sweater (optional)"]
            recommendation["layers"]["outer"] = ["Light jacket"]
            recommendation["accessories"] = []
            recommendation["footwear"] = ["Sneakers", "Casual shoes"]
            recommendation["tips"] = [
                "Perfect for outdoor activities",
                "Bring a light layer for evening"
            ]
            
        elif 18 <= temp < 25:
            recommendation["summary"] = "☀️ Pleasant weather. Dress comfortably."
            recommendation["layers"]["base"] = ["T-shirt", "Light shirt"]
            recommendation["layers"]["mid"] = []
            recommendation["layers"]["outer"] = ["Light jacket (optional)"]
            recommendation["accessories"] = ["Sunglasses"]
            recommendation["footwear"] = ["Sneakers", "Sandals"]
            recommendation["tips"] = [
                "Great weather for outdoor activities",
                "May cool down in evening"
            ]
            
        elif 25 <= temp < 30:
            recommendation["summary"] = "🌞 Warm weather. Light and breathable clothing."
            recommendation["layers"]["base"] = ["Light t-shirt", "Tank top"]
            recommendation["layers"]["mid"] = []
            recommendation["layers"]["outer"] = []
            recommendation["accessories"] = ["Sunglasses", "Sun hat"]
            recommendation["footwear"] = ["Sandals", "Light sneakers"]
            recommendation["tips"] = [
                "Wear light colors to stay cool",
                "Stay hydrated",
                "Seek shade during peak hours"
            ]
            
        else:  # >= 30
            recommendation["summary"] = "🔥 Very hot! Stay cool and protected."
            recommendation["layers"]["base"] = ["Lightweight breathable shirt"]
            recommendation["layers"]["mid"] = []
            recommendation["layers"]["outer"] = []
            recommendation["accessories"] = ["Wide-brim hat", "Sunglasses"]
            recommendation["footwear"] = ["Sandals", "Breathable shoes"]
            recommendation["tips"] = [
                "Wear loose, light-colored clothing",
                "Drink water frequently",
                "Avoid outdoor activities during midday",
                "Apply sunscreen regularly"
            ]
        
        # Precipitation adjustments
        if precip > 0:
            recommendation["accessories"].append("Umbrella")
            recommendation["tips"].insert(0, "☔ Rain expected - bring waterproof gear")
            
            if precip > 5:
                recommendation["layers"]["outer"].append("Waterproof jacket")
                recommendation["footwear"] = ["Waterproof boots"]
                recommendation["tips"].insert(0, "🌧️ Heavy rain - dress waterproof")
        
        # Wind adjustments
        if wind_speed > 20:
            recommendation["tips"].append(f"💨 Windy ({wind_speed} km/h) - secure loose items")
            if temp < 15:
                recommendation["tips"].append("Wind chill will make it feel colder")
        
        # UV protection
        if uv_index >= 6:
            if "Sunglasses" not in recommendation["accessories"]:
                recommendation["accessories"].append("Sunglasses")
            recommendation["tips"].append(f"☀️ High UV ({uv_index}) - wear sunscreen SPF 30+")
        
        return recommendation


# Singleton instance
fashion_service = FashionService()