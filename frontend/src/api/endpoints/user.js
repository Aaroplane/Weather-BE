import apiClient from '../client';

// USER SESSION HELPER
/**
 * Get or generate user session ID from localStorage
 * @returns {string} User ID
 */
const getUserId = () => {
  const USER_ID_KEY = 'weather_agent_user_id';
  let userId = localStorage.getItem(USER_ID_KEY);
  
  if (!userId) {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 11);
    userId = `user_${timestamp}_${random}`;
    localStorage.setItem(USER_ID_KEY, userId);
    console.log('✅ New user session created:', userId);
  }
  
  return userId;
};

// USER API ENDPOINTS

export const userAPI = {
  /**
   * Get weather by GPS coordinates (for "Use My Location")
   * @param {number} latitude
   * @param {number} longitude
   * @returns {Promise}
   */
  getWeatherByCoords: async (latitude, longitude) => {
    const { data } = await apiClient.post('/api/weather/by-coords', {
      latitude,
      longitude,
      user_id: getUserId()
    });
    return data;
  },

  /**
   * Get fashion recommendations based on weather
   * @param {Object} weatherData - {temperature, precipitation, wind_speed, uv_index}
   * @returns {Promise}
   */
  getFashionRecommendations: async (weatherData) => {
    const { data } = await apiClient.post('/api/fashion/recommendations', {
      temperature: weatherData.temperature,
      precipitation: weatherData.precipitation,
      wind_speed: weatherData.wind_speed,
      uv_index: weatherData.uv_index
    });
    return data;
  },

  /**
   * Submit fashion feedback
   * @param {Object} weatherConditions
   * @param {Array} tipsShown
   * @param {string} feedback - 'helpful' | 'not_helpful' | 'ignored'
   * @returns {Promise}
   */
  submitFashionFeedback: async (weatherConditions, tipsShown, feedback) => {
    const { data } = await apiClient.post('/api/feedback/fashion', {
      user_id: getUserId(),
      weather_conditions: weatherConditions,
      tips_shown: tipsShown,
      feedback: feedback
    });
    return data;
  },

  /**
   * Save user preference to backend
   * @param {string} preferenceType - 'temp_unit' | 'theme' | etc.
   * @param {string} value
   * @returns {Promise}
   */
  savePreference: async (preferenceType, value) => {
    const { data } = await apiClient.post('/api/preferences', {
      user_id: getUserId(),
      preference_type: preferenceType,
      value: value,
      context: 'manual'
    });
    
    // Also save to localStorage for immediate access
    const prefs = userAPI.getLocalPreferences();
    prefs[preferenceType] = value;
    localStorage.setItem('weather_agent_preferences', JSON.stringify(prefs));
    
    return data;
  },

  /**
   * Get user preferences from backend
   * @returns {Promise}
   */
  getPreferences: async () => {
    try {
      const userId = getUserId();
      const { data } = await apiClient.get(`/api/preferences/${userId}`);
      return data.preferences;
    } catch (error) {
      console.error('❌ Error fetching preferences:', error);
      return {};
    }
  },

  /**
   * Get preferences from localStorage (no API call)
   * @returns {Object}
   */
  getLocalPreferences: () => {
    try {
      const prefs = localStorage.getItem('weather_agent_preferences');
      return prefs ? JSON.parse(prefs) : {};
    } catch (error) {
      console.error('❌ Failed to parse local preferences:', error);
      return {};
    }
  },

  /**
   * Get user's recent location searches
   * @param {number} limit
   * @returns {Promise}
   */
  getRecentLocations: async (limit = 5) => {
    try {
      const userId = getUserId();
      const { data } = await apiClient.get(`/api/locations/recent/${userId}`, {
        params: { limit }
      });
      return data.locations;
    } catch (error) {
      console.error('❌ Error fetching recent locations:', error);
      return [];
    }
  },
};