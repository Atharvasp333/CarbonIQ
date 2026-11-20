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
      .then(async (res) => {
        const userData = res.data?.user || res.data;
        // Enrich with organization from organization_profile if not already set
        try {
          const orgRes = await axios.get(`${API_BASE}/api/profile/`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          if (orgRes.data?.organization_name) {
            userData.organization = orgRes.data.organization_name;
          }
        } catch (_) {}
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

    let updatedUser = { ...user, ...updates };

    // 1. Try dedicated PUT /api/auth/profile
    try {
      const response = await axios.put(`${API_BASE}/api/auth/profile`, updates, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data?.user) {
        updatedUser = response.data.user;
      }
    } catch (err) {
      console.warn('PUT /api/auth/profile fallback needed:', err?.message);
    }

    // 2. Persist organization to /api/profile/ (guaranteed supported in live database)
    if (updates.organization) {
      try {
        await axios.post(`${API_BASE}/api/profile/`, {
          organization_name: updates.organization,
          primary_user_region: 'Global',
          workload_type: 'Mixed',
          latency_sensitivity: 'Medium',
          migration_flexibility: 'Some Workloads',
          optimization_priority: 'Reduce Carbon'
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } catch (orgErr) {
        console.warn('Organization profile sync warning:', orgErr?.message);
      }
    }

    setUser(updatedUser);
    return { success: true, user: updatedUser };
  };

  return (
    <AuthContext.Provider
      value={{ user, loading, login, signup, logout, updateProfile, isAuthenticated: !!user }}
    >
      {!loading && children}
    </AuthContext.Provider>
  );
};
