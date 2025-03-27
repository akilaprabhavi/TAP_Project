import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Dashboard from './pages/dashboard';
import Category from './pages/category-page';
import AddPrompts from './pages/AddPrompts-page';

const AppRouter = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/category" element={<Category />} />
        <Route path="/AddPrompts" element={<AddPrompts />} />
      </Routes>
    </Router>
  );
};

export default AppRouter;
