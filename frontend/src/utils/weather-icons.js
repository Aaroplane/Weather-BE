/**
 * Get weather icon based on conditions
 */
export const getWeatherIcon = (temperature, precipitation) => {
  if (precipitation > 5) return '⛈️';
  if (precipitation > 0) return '🌧️';
  if (temperature < 0) return '❄️';
  if (temperature < 10) return '🌥️';
  if (temperature < 20) return '⛅';
  if (temperature < 30) return '☀️';
  return '🔥';
};

/**
 * Get condition description
 */
export const getConditionText = (temperature, precipitation) => {
  if (precipitation > 5) return 'Heavy Rain';
  if (precipitation > 0) return 'Light Rain';
  if (temperature < 0) return 'Freezing';
  if (temperature < 10) return 'Cold';
  if (temperature < 20) return 'Cool';
  if (temperature < 25) return 'Pleasant';
  if (temperature < 30) return 'Warm';
  return 'Hot';
};