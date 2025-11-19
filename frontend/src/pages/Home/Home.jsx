import { useState, useEffect } from 'react';
import { SearchBar } from '../../components/location/SearchBar/SearchBar.jsx';
import { WeatherCard } from '../../components/weather/WeatherCard/WeatherCard.jsx';
import { SuggestionCard } from '../../components/weather/SuggestionCard/SuggestionCard.jsx';
import { Spinner } from '../../components/common/Spinner/Spinner.jsx';
import { Button } from '../../components/common/Button/Button.jsx';
import TemperatureToggle from '../../components/TemperatureToggle/TemperatureToggle.jsx';
import UseMyLocation from '../../components/location/UseMyLocation/UseMyLocation.jsx';
import FashionTips from '../../components/weather/FashionTips/FashionTips.jsx';
import { useWeather } from '../../hooks/useWeather.js';
import { userAPI } from '../../api/endpoints/user.js';
import { getUserPreferences, saveUserPreference } from '../../utils/userSessions.js';
import styles from './Home.module.scss';

export const Home = () => {
  const { weather, loading, error, fetchWeather, reset } = useWeather();
  const [hasSearched, setHasSearched] = useState(false);
  const [tempUnit, setTempUnit] = useState('C');

  useEffect(() => {
    const savedUnit = getUserPreferences('temp_unit', 'C');
    setTempUnit(savedUnit);
  }, []);

  const handleSearch = async (location) => {
    setHasSearched(true);
    try {
      await fetchWeather(location);
    } catch (err) {
      console.error('Search failed:', err);
    }
  };

  const handleLocationDetected = async (weatherData) => {
    setHasSearched(true);
    // useWeather hook might not have a direct setter, 
    // so we'll fetch using the location name
    if (weatherData?.location?.location_name) {
      await fetchWeather(weatherData.location.location_name);
    }
  };

  const handleTempToggle = async (newUnit) => {
    setTempUnit(newUnit);
    saveUserPreference('temp_unit', newUnit);
    
    // Also save to backend
    try {
      await userAPI.savePreference('temp_unit', newUnit);
      console.log('✅ Temperature preference saved to backend');
    } catch (err) {
      console.error('❌ Failed to save temp preference to backend:', err);
    }
  };

  const handleReset = () => {
    reset();
    setHasSearched(false);
  };

  // Convert temperature based on unit
  const convertTemp = (celsius) => {
    if (tempUnit === 'F') {
      return (celsius * 9/5 + 32).toFixed(1);
    }
    return celsius.toFixed(1);
  };

  return (
    <div className={styles.home}>
      <div className={styles.container}>
        {/* Header with Temperature Toggle */}
        <header className={styles.header}>
          <div className={styles.headerContent}>
            <div className={styles.titleSection}>
              <h1 className={styles.title}>
                <span className={styles.icon}>🌤️</span>
                Weather Agent
              </h1>
              <p className={styles.subtitle}>
                AI-powered weather monitoring and suggestions
              </p>
            </div>
            <div className={styles.headerControls}>
              <TemperatureToggle 
                unit={tempUnit} 
                onToggle={handleTempToggle}
              />
            </div>
          </div>
        </header>

        {/* Search Bar + Use My Location */}
        <div className={styles.searchSection}>
          <SearchBar onSearch={handleSearch} loading={loading} />
          <UseMyLocation 
            onLocationDetected={handleLocationDetected}
            disabled={loading}
          />
        </div>

        {/* Loading State */}
        {loading && (
          <div className={styles.loading}>
            <Spinner size="lg" color="white" />
            <p className={styles.loadingText}>Fetching weather data...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className={styles.error}>
            <span className={styles.errorIcon}>⚠️</span>
            <div className={styles.errorContent}>
              <h3 className={styles.errorTitle}>Oops! Something went wrong</h3>
              <p className={styles.errorMessage}>{error}</p>
              <Button onClick={handleReset} variant="outline">
                Try Again
              </Button>
            </div>
          </div>
        )}

        {/* Weather Display */}
        {weather && !loading && !error && (
          <div className={styles.weatherSection}>
            <WeatherCard 
              weather={weather}
              tempUnit={tempUnit}
              convertTemp={convertTemp}
            />

            {/* Fashion Tips - NEW */}
            <FashionTips 
              weatherData={{
                temperature: weather.current_weather.temperature,
                precipitation: weather.current_weather.precipitation,
                wind_speed: weather.current_weather.wind_speed,
                uv_index: weather.current_weather.uv_index
              }}
            />

            {/* Suggestions */}
            {weather.suggestions && weather.suggestions.length > 0 && (
              <div className={styles.suggestions}>
                <h3 className={styles.suggestionsTitle}>
                  💡 Weather Suggestions
                </h3>
                <div className={styles.suggestionsList}>
                  {weather.suggestions.map((suggestion, index) => (
                    <SuggestionCard key={index} suggestion={suggestion} />
                  ))}
                </div>
              </div>
            )}

            {/* Search Again Button */}
            <div className={styles.actions}>
              <Button onClick={handleReset} variant="ghost">
                🔍 Search Another Location
              </Button>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!hasSearched && !loading && (
          <div className={styles.emptyState}>
            <span className={styles.emptyIcon}>🌍</span>
            <h3 className={styles.emptyTitle}>Search for any location</h3>
            <p className={styles.emptyText}>
              Get real-time weather data and personalized suggestions
            </p>
          </div>
        )}
      </div>
    </div>
  );
};