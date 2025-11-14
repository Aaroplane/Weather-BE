import { useState } from 'react';
import { SearchBar } from '../../components/location/SearchBar/SearchBar.jsx';
import { WeatherCard } from '../../components/weather/WeatherCard/WeatherCard.jsx';
import { SuggestionCard } from '../../components/weather/SuggestionCard/SuggestionCard.jsx';
import { Spinner } from '../../components/common/Spinner/Spinner.jsx';
import { Button } from '../../components/common/Button/Button.jsx';
import { useWeather } from '../../hooks/useWeather.js';
import styles from './Home.module.scss';

export const Home = () => {
  const { weather, loading, error, fetchWeather, reset } = useWeather();
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (location) => {
    setHasSearched(true);
    try {
      await fetchWeather(location);
    } catch (err) {
      // Error is already handled in useWeather hook
      console.error('Search failed:', err);
    }
  };

  const handleReset = () => {
    reset();
    setHasSearched(false);
  };

  return (
    <div className={styles.home}>
      <div className={styles.container}>
        {/* Header */}
        <header className={styles.header}>
          <h1 className={styles.title}>
            <span className={styles.icon}>🌤️</span>
            Weather Agent
          </h1>
          <p className={styles.subtitle}>
            AI-powered weather monitoring and suggestions
          </p>
        </header>

        {/* Search Bar */}
        <SearchBar onSearch={handleSearch} loading={loading} />

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
            <WeatherCard weather={weather} />

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