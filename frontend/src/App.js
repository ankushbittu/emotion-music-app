import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useLocation } from 'react-router-dom';
import Register from './Register';
import Login from './Login';
import Dashboard from './Dashboard';
import ProtectedRoute from './ProtectedRoute'; // Import the protected route component
import './App.css';

function App() {
  const token = localStorage.getItem('token'); // Check if user is logged in
  const location = useLocation(); // Get the current route

  return (
    <div>
      {/* Conditionally show navbar */}
      {!location.pathname.includes('/dashboard') && (
        <nav>
          <ul>
            {!token ? (
              <>
                {location.pathname !== '/register' && (
                  <li>
                    <Link to="/register">Register</Link>
                  </li>
                )}
                {location.pathname !== '/login' && (
                  <li>
                    <Link to="/login">Login</Link>
                  </li>
                )}
              </>
            ) : (
              <li>
                <Link to="/login" onClick={() => localStorage.removeItem('token')}>
                  Logout
                </Link>
              </li>
            )}
          </ul>
        </nav>
      )}

      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={<ProtectedRoute element={<Dashboard />} />} // Use ProtectedRoute
        />
        <Route path="/" element={<h1>Welcome! Please register or login. @AMR.</h1>} />
      </Routes>
    </div>
  );
}

export default function AppWithRouter() {
  return (
    <Router>
      <App />
    </Router>
  );
}
