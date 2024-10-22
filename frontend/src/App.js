import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useNavigate } from 'react-router-dom';
import Register from './Register';
import Login from './Login';
import Dashboard from './Dashboard';
import './App.css';

function App() {
  const token = localStorage.getItem('token');  // Check if user is logged in

  const handleLogout = () => {
    localStorage.removeItem('token');  // Remove JWT token on logout
  };

  return (
    <Router>
      <div>
        <nav>
          <ul>
            {!token && (
              <>
                <li>
                  <Link to="/register">Register</Link>
                </li>
                <li>
                  <Link to="/login">Login</Link>
                </li>
              </>
            )}
            {token && (
              <>
                <li>
                  <Link to="/dashboard">Dashboard</Link>
                </li>
                <li>
                  <Link to="/login" onClick={handleLogout}>Logout</Link>
                </li>
              </>
            )}
          </ul>
        </nav>

        <Routes>
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/" element={<h1>Welcome! Please register or login.</h1>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
