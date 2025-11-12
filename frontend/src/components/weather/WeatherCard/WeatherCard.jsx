import { formatTemperature, formatWindSpeed } from '../../../utils/formatters';
import { getWeatherIcon, getConditionText } from '../../../utils/weather-icons';
import styles from './WeatherCard.module.scss';

export const WeatherCard = ({ weather }) => {
  const { current_weather, location } = weather;
  
  const icon = getWeatherIcon(
    current_weather.temperature,
    current_weather.precipitation
  );
  
  const condition = getConditionText(
    current_weather.temperature,
    current_weather.precipitation
  );

  return (
    <div className={styles.card}>
      {/* Location Header */}
      <div className={styles.header}>
        <h2 className={styles.locationName}>
          {location.short_name}
        </h2>
        <p className={styles.locationDetails}>
          {location.location_name}
        </p>
      </div>

      {/* Main Weather */}
      <div className={styles.mainWeather}>
        <div className={styles.tempSection}>
          <div className={styles.temperature}>
            {formatTemperature(current_weather.temperature)}
          </div>
          <div className={styles.condition}>
            {condition}
          </div>
        </div>
        <div className={styles.icon}>
          {icon}
        </div>
      </div>

      {/* Details Grid */}
      <div className={styles.detailsGrid}>
        <DetailItem 
          icon="💨" 
          label="Wind" 
          value={formatWindSpeed(current_weather.wind_speed)} 
        />
        <DetailItem 
          icon="💧" 
          label="Humidity" 
          value={`${current_weather.humidity}%`} 
        />
        <DetailItem 
          icon="🌧️" 
          label="Precipitation" 
          value={`${current_weather.precipitation} mm`} 
        />
        <DetailItem 
          icon="☀️" 
          label="UV Index" 
          value={current_weather.uv_index} 
        />
      </div>
    </div>
  );
};

// Sub-component
const DetailItem = ({ icon, label, value }) => (
  <div className={styles.detailItem}>
    <div className={styles.detailLabel}>
      <span className={styles.detailIcon}>{icon}</span>
      <span>{label}</span>
    </div>
    <div className={styles.detailValue}>
      {value}
    </div>
  </div>
);