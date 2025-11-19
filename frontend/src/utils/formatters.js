/**
 * Format temperature with unit
    */
// export const formatTemperature = (celsius, unit = 'C') => {
//   if (unit === 'F') {
//     const fahrenheit = (celsius * 9/5) + 32;
//     return `${fahrenheit.toFixed(1)}°F`;
//   }
//   return `${celsius.toFixed(1)}°C`;
// };

export const formatWindSpeed = (kmh) => {
  return `${kmh.toFixed(1)} km/h`;
};

export const formatTimestamp = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};