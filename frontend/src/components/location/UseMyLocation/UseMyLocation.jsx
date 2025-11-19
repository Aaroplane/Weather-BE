import { useState } from 'react';
import { userAPI } from '../../../api/endpoints/user';
import { Button } from '../../common/Button/Button';
import styles from './UseMyLocation.module.scss';

const UseMyLocation = ({ onLocationDetected, disabled = false }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGetLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      return;
    }

    setLoading(true);
    setError(null);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords;
          console.log('📍 Location detected:', { latitude, longitude });
          
          const weatherData = await userAPI.getWeatherByCoords(latitude, longitude);
          console.log('✅ Weather fetched for location:', weatherData);
          
          onLocationDetected(weatherData);
          setLoading(false);
        } catch (err) {
          console.error('❌ Failed to fetch weather:', err);
          setError('Failed to fetch weather for your location');
          setLoading(false);
        }
      },
      (error) => {
        let errorMessage = 'Unable to get your location';
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location access denied. Please enable location permissions.';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information unavailable.';
            break;
          case error.TIMEOUT:
            errorMessage = 'Location request timed out.';
            break;
          default:
            errorMessage = 'An unknown error occurred.';
        }
        
        console.error('❌ Geolocation error:', error);
        setError(errorMessage);
        setLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  };

  const handleMockLocation = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Mock coordinates for New York City
      const mockLatitude = 40.7128;
      const mockLongitude = -74.0060;
      
      console.log('🧪 Using mock location:', { mockLatitude, mockLongitude });
      
      const weatherData = await userAPI.getWeatherByCoords(mockLatitude, mockLongitude);
      console.log('✅ Weather fetched for mock location:', weatherData);
      
      onLocationDetected(weatherData);
      setLoading(false);
    } catch (err) {
      console.error('❌ Failed to fetch weather:', err);
      setError('Failed to fetch weather for mock location');
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.buttonGroup}>
        <Button
          variant="secondary"
          size="md"
          loading={loading}
          disabled={disabled}
          onClick={handleGetLocation}
          className={styles.locationButton}
        >
          {!loading && <span className={styles.icon}>📍</span>}
          <span>Use My Location</span>
        </Button>
        
        <Button
          variant="secondary"
          size="md"
          loading={loading}
          disabled={disabled}
          onClick={handleMockLocation}
          className={styles.mockButton}
        >
          {!loading && <span className={styles.icon}>🧪</span>}
          <span>Mock NYC</span>
        </Button>
      </div>
      
      {error && (
        <div className={styles.error}>
          ⚠️ {error}
        </div>
      )}
    </div>
  );
};

export default UseMyLocation;