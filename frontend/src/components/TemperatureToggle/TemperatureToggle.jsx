import React from 'react';
import styles from './TemperatureToggle.module.scss';

/**
 * Temperature unit toggle component (Celsius ↔ Fahrenheit)
 * Phase 1.5: Manual toggle with preference saving
 * Phase 3: Auto-detect based on location/history
 */
const TemperatureToggle = ({ unit, onToggle }) => {
  const handleToggle = () => {
    const newUnit = unit === 'C' ? 'F' : 'C';
    onToggle(newUnit);
  };

  return (
    <div className={styles.toggleContainer}>
      <button
        className={styles.toggleButton}
        onClick={handleToggle}
        aria-label={`Switch to ${unit === 'C' ? 'Fahrenheit' : 'Celsius'}`}
        title={`Currently showing ${unit === 'C' ? 'Celsius' : 'Fahrenheit'}`}
      >
        <span className={unit === 'C' ? styles.active : styles.inactive}>°C</span>
        <span className={styles.divider}>|</span>
        <span className={unit === 'F' ? styles.active : styles.inactive}>°F</span>
      </button>
    </div>
  );
};

export default TemperatureToggle;