import { createContext, useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('auth_token');
    if (token) {
      axios.get(`${API_BASE}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => {
        const userData = res.data?.user || res.data;
        setUser(userData);
        setLoading(false);
      })
      .catch((err) => {
        if (err.response?.status === 401) {
          localStorage.removeItem('auth_token');
          setUser(null);
        }
        setLoading(false);
      });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API_BASE}/api/auth/login`, {
        email,
        password
      });
      
      const { access_token, user: userData } = response.data;
      localStorage.setItem('auth_token', access_token);
      setUser(userData);
      return { success: true };
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed';
      return { success: false, error: message };
    }
  };

  const signup = async ({ name, email, password }) => {
    try {
      const response = await axios.post(`${API_BASE}/api/auth/signup`, {
        name,
        email,
        password
      });
      
      const { access_token, user: userData } = response.data;
      localStorage.setItem('auth_token', access_token);
      setUser(userData);
      return { success: true };
    } catch (err) {
      const message = err.response?.data?.detail || 'Signup failed';
      return { success: false, error: message };
    }
  };

  const logout = async () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('awsAnalysisData');
    localStorage.removeItem('hasLoadedData');
    setUser(null);
  };

  const updateProfile = async (updates) => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      setUser((prev) => ({ ...prev, ...updates }));
      return { success: true };
    }

    try {
      const response = await axios.put(`${API_BASE}/api/auth/profile`, updates, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const updatedUser = response.data?.user || { ...user, ...updates };
      setUser(updatedUser);
      return { success: true, user: updatedUser };
    } catch (err) {
      console.error('Failed to update profile on backend:', err);
      setUser((prev) => ({ ...prev, ...updates }));
      const msg = err.response?.data?.detail || 'Failed to persist profile to server';
      return { success: false, error: msg };
    }
  };

  return (
    <AuthContext.Provider
      value={{ user, loading, login, signup, logout, updateProfile, isAuthenticated: !!user }}
    >
      {!loading && children}
    </AuthContext.Provider>
  );
};
