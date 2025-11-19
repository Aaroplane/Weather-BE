/* User Sessions Utility Module Persisting Id for Session */

const USER_ID_KEY = 'weather_agent_user_id';

export const getUserId = () => {
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

export const clearUserSession = () => {
  localStorage.removeItem(USER_ID_KEY);
  console.log('🗑️ User session cleared');
};

export const getUserPreferences = () => {
  const prefs = localStorage.getItem('weather_agent_preferences');
  return prefs ? JSON.parse(prefs) : {};
};

/**
 * @param {string} key - Preference key
 * @param {any} value - Preference value
 */
export const saveUserPreference = (key, value) => {
  const prefs = getUserPreferences();
  prefs[key] = value;
  localStorage.setItem('weather_agent_preferences', JSON.stringify(prefs));
  console.log(`✅ Saved preference: ${key} = ${value}`);
};

export const removePreference = (key) => {
  const prefs = getUserPreferences();
  delete prefs[key];
  localStorage.setItem(PREFERENCES_KEY, JSON.stringify(prefs));
  console.log(`🗑️ Removed preference: ${key}`);
};