import { createContext, useEffect, useState } from 'react';
import { authClient } from '../lib/auth';
import { syncUser } from '../api/client';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    authClient.getSession().then(({ data }) => {
      const u = data?.user ?? null;
      setUser(u);
      
      // Try multiple possible token locations
      let token = null;
      
      if (data?.session?.access_token) {
        token = data.session.access_token;
        console.log('[AUTH] Token found at: data.session.access_token');
      } else if (data?.access_token) {
        token = data.access_token;
        console.log('[AUTH] Token found at: data.access_token');
      } else if (data?.token) {
        token = data.token;
        console.log('[AUTH] Token found at: data.token');
      } else if (data?.session?.token) {
        token = data.session.token;
        console.log('[AUTH] Token found at: data.session.token');
      }
      
      if (token) {
        localStorage.setItem('auth_token', token);
        console.log('[AUTH] Token stored from session');
      }
      
      // Sync to our users table silently
      if (u?.email) syncUser(u.email, u.name).catch(() => {});
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    try {
      const result = await authClient.signIn.email({ email, password });
      if (result.error) return { success: false, error: result.error.message };
      
      const { data } = await authClient.getSession();
      const u = data?.user ?? null;
      setUser(u);
      
      // Debug: Log the entire session structure to find the token
      console.log('[AUTH DEBUG] Full session data:', data);
      console.log('[AUTH DEBUG] Session keys:', Object.keys(data || {}));
      if (data?.session) {
        console.log('[AUTH DEBUG] Session object keys:', Object.keys(data.session));
      }
      
      // Try multiple possible token locations
      let token = null;
      
      // Location 1: data.session.access_token (standard)
      if (data?.session?.access_token) {
        token = data.session.access_token;
        console.log('[AUTH] Token found at: data.session.access_token');
      }
      // Location 2: data.access_token
      else if (data?.access_token) {
        token = data.access_token;
        console.log('[AUTH] Token found at: data.access_token');
      }
      // Location 3: data.token
      else if (data?.token) {
        token = data.token;
        console.log('[AUTH] Token found at: data.token');
      }
      // Location 4: data.session.token
      else if (data?.session?.token) {
        token = data.session.token;
        console.log('[AUTH] Token found at: data.session.token');
      }
      // Location 5: Use fallback to backend JWT
      else {
        console.warn('[AUTH] No access token in Neon session - will use backend JWT');
        // Call backend login to get our own JWT
        try {
          const backendLogin = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
          });
          const backendData = await backendLogin.json();
          if (backendData.token) {
            token = backendData.token;
            console.log('[AUTH] Token obtained from backend /api/auth/login');
          }
        } catch (err) {
          console.error('[AUTH] Backend login failed:', err);
        }
      }
      
      if (token) {
        localStorage.setItem('auth_token', token);
        console.log('[AUTH] ✓ Token stored successfully');
      } else {
        console.error('[AUTH] ✗ No token found anywhere - authentication may fail');
      }
      
      if (u?.email) syncUser(u.email, u.name).catch(() => {});
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || 'Login failed' };
    }
  };

  const signup = async ({ name, email, password }) => {
    try {
      const result = await authClient.signUp.email({ name, email, password });
      if (result.error) return { success: false, error: result.error.message };
      
      const { data } = await authClient.getSession();
      const u = data?.user ?? null;
      setUser(u);
      
      // Try multiple possible token locations
      let token = null;
      
      if (data?.session?.access_token) {
        token = data.session.access_token;
        console.log('[AUTH] Token found at: data.session.access_token');
      } else if (data?.access_token) {
        token = data.access_token;
        console.log('[AUTH] Token found at: data.access_token');
      } else if (data?.token) {
        token = data.token;
        console.log('[AUTH] Token found at: data.token');
      } else if (data?.session?.token) {
        token = data.session.token;
        console.log('[AUTH] Token found at: data.session.token');
      } else {
        console.warn('[AUTH] No access token in Neon session - will use backend JWT');
        // Call backend signup to get our own JWT
        try {
          const backendSignup = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
          });
          const backendData = await backendSignup.json();
          if (backendData.token) {
            token = backendData.token;
            console.log('[AUTH] Token obtained from backend /api/auth/signup');
          }
        } catch (err) {
          console.error('[AUTH] Backend signup failed:', err);
        }
      }
      
      if (token) {
        localStorage.setItem('auth_token', token);
        console.log('[AUTH] ✓ Token stored successfully');
      } else {
        console.error('[AUTH] ✗ No token found anywhere - authentication may fail');
      }
      
      if (u?.email) syncUser(u.email, u.name || name).catch(() => {});
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || 'Signup failed' };
    }
  };

  const logout = async () => {
    await authClient.signOut();
    localStorage.removeItem('neon_jwt');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('awsAnalysisData');
    localStorage.removeItem('hasLoadedData');
    setUser(null);
  };

  const updateProfile = (updates) => {
    setUser((prev) => ({ ...prev, ...updates }));
  };

  return (
    <AuthContext.Provider
      value={{ user, loading, login, signup, logout, updateProfile, isAuthenticated: !!user }}
    >
      {!loading && children}
    </AuthContext.Provider>
  );
};
