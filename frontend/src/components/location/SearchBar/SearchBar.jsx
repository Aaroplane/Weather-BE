import { useState } from 'react';
import { Input } from '../../common/Input/Input';
import { Button } from '../../common/Button/Button';
import styles from './SearchBar.module.scss';

export const SearchBar = ({ onSearch, loading = false }) => {
  const [location, setLocation] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (location.trim()) {
      onSearch(location.trim());
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  return (
    <form className={styles.searchBar} onSubmit={handleSubmit}>
      <Input
        type="text"
        placeholder="Search location (e.g., Brooklyn, Paris, Tokyo...)"
        value={location}
        onChange={(e) => setLocation(e.target.value)}
        onKeyPress={handleKeyPress}
        leftIcon="🔍"
        disabled={loading}
        className={styles.input}
      />
      <Button 
        type="submit" 
        loading={loading}
        disabled={!location.trim() || loading}
      >
        Search
      </Button>
    </form>
  );
};