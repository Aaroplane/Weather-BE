import React, { useState } from 'react';
import TemperatureToggle from '../components/TemperatureToggle/TemperatureToggle';
import FashionTips from '../components/weather/FashionTips/FashionTips';
import { saveUserPreference, getUserId } from '../utils/userSessions';

const TestPage = () => {
  const [unit, setUnit] = useState('C');

  const handleToggle = (newUnit) => {
    setUnit(newUnit);
    saveUserPreference('temp_unit', newUnit);
    console.log('✅ Temperature unit changed to:', newUnit);
  };

  // Mock weather data for testing FashionTips
  const mockWeatherData = {
    temperature: 5,
    precipitation: 0,
    wind_speed: 10,
    uv_index: 2
  };

  return (
    <div style={{ 
      padding: '2rem', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      minHeight: '100vh',
      color: 'white'
    }}>
      <h1>🧪 Phase 1.5 Component Tests</h1>
      
      <div style={{ marginBottom: '2rem', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
        <h3>Session Info</h3>
        <p><strong>User ID:</strong> <code>{getUserId()}</code></p>
        <p><strong>Check localStorage:</strong> Open DevTools → Application → Local Storage</p>
      </div>

      <hr style={{ margin: '2rem 0', border: '1px solid rgba(255,255,255,0.2)' }} />

      {/* TEST 1: Temperature Toggle */}
      <div style={{ marginBottom: '3rem' }}>
        <h2>1️⃣ Temperature Toggle Test</h2>
        <p>Current unit: <strong style={{ fontSize: '1.5rem' }}>{unit}</strong></p>
        
        <div style={{ marginTop: '1rem' }}>
          <TemperatureToggle unit={unit} onToggle={handleToggle} />
        </div>

        <div style={{ marginTop: '1rem', fontSize: '0.9rem', opacity: 0.8 }}>
          <p>✅ Click toggle to switch between °C and °F</p>
          <p>✅ Check console for "preference saved" log</p>
          <p>✅ Check localStorage for "weather_agent_preferences"</p>
        </div>
      </div>

      <hr style={{ margin: '2rem 0', border: '1px solid rgba(255,255,255,0.2)' }} />

      {/* TEST 2: Fashion Tips */}
      <div style={{ marginBottom: '3rem' }}>
        <h2>2️⃣ Fashion Tips Test</h2>
        <p>Testing with 5°C cold weather</p>
        
        <FashionTips weatherData={mockWeatherData} />

        <div style={{ marginTop: '1rem', fontSize: '0.9rem', opacity: 0.8 }}>
          <p>✅ Should show cold weather recommendations</p>
          <p>✅ Click header to expand/collapse</p>
          <p>✅ Click feedback buttons (check Network tab for API call)</p>
        </div>
      </div>

      <hr style={{ margin: '2rem 0', border: '1px solid rgba(255,255,255,0.2)' }} />

      {/* TEST 3: Different Weather */}
      <div style={{ marginBottom: '3rem' }}>
        <h2>3️⃣ Fashion Tips - Hot Weather Test</h2>
        <FashionTips weatherData={{
          temperature: 32,
          precipitation: 0,
          wind_speed: 5,
          uv_index: 9
        }} />

        <div style={{ marginTop: '1rem', fontSize: '0.9rem', opacity: 0.8 }}>
          <p>✅ Should show hot weather recommendations</p>
          <p>✅ Should mention UV protection</p>
        </div>
      </div>

      <hr style={{ margin: '2rem 0', border: '1px solid rgba(255,255,255,0.2)' }} />

      <div style={{ padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
        <h3>🔍 Debugging Checklist</h3>
        <ol style={{ lineHeight: '1.8' }}>
          <li>Open DevTools Console (check for errors)</li>
          <li>Open DevTools Network tab (check API calls)</li>
          <li>Open DevTools Application → Local Storage</li>
          <li>Backend running? <code>http://localhost:8000/docs</code></li>
        </ol>
      </div>

      <div style={{ marginTop: '2rem', textAlign: 'center' }}>
        <a href="/" style={{ 
          color: 'white', 
          textDecoration: 'underline',
          fontSize: '1.1rem'
        }}>
          ← Back to Home
        </a>
      </div>
    </div>
  );
};

export default TestPage;