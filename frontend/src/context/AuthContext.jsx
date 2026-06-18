import { createContext, useEffect, useState } from 'react';
import { authClient } from '../lib/auth';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Restore session on mount
    authClient.getSession().then(({ data }) => {
      setUser(data?.user ?? null);
      setLoading(false);
    });
  }, []);

  const login = async (email, password) => {
    try {
      const result = await authClient.signIn.email({ email, password });
      if (result.error) return { success: false, error: result.error.message };
      const { data } = await authClient.getSession();
      setUser(data?.user ?? null);
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
      setUser(data?.user ?? null);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || 'Signup failed' };
    }
  };

  const logout = async () => {
    await authClient.signOut();
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
