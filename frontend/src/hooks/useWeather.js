import { useState, useCallback } from 'react';
import { weatherAPI } from '../api/endpoints/weather';


export const useWeather = () => {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchWeather = useCallback(async (location) => {
    setLoading(true);
    setError(null);

    try {
      const data = await weatherAPI.getCurrent(location);
      setWeather(data);
      return data;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to fetch weather data';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setWeather(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    weather,
    loading,
    error,
    fetchWeather,
    reset,
  };
};