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
      if (u?.email) syncUser(u.email, u.name || name).catch(() => {});
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || 'Signup failed' };
    }
  };

  const logout = async () => {
    await authClient.signOut();
    localStorage.removeItem('neon_jwt');
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
