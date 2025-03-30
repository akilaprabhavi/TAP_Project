import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Dashboard from './pages/dashboard';
import Category from './pages/category-page';
import DailyUpdates from './pages/DailyUpdates-page';
import AttackVectors from './pages/category-page';

const AppRouter = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/category" element={<Category />} />
        <Route path="/dailyUpdates" element={<DailyUpdates />} />
        <Route path="/AttackVectors" element={<AttackVectors />} />
      </Routes>
    </Router>
  );
};

export default AppRouter;
