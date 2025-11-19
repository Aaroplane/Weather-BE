import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Home } from './pages/Home/Home';
import TestPage from './pages/Tests';
import styles from './App.module.scss';

function App() {
  return (
    <div className={styles.app}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/test" element={<TestPage />} />
      </Routes>
    </div>
  );
}

export default App;