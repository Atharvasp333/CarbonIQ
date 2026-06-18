import { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('carboniq_user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        localStorage.removeItem('carboniq_user');
      }
    }
    setLoading(false);
  }, []);

  const login = (email, password) => {
    // Simulate authentication (in production, call real API)
    const users = JSON.parse(localStorage.getItem('carboniq_users') || '[]');
    const user = users.find(u => u.email === email && u.password === password);
    
    if (user) {
      const { password, ...userWithoutPassword } = user;
      setUser(userWithoutPassword);
      localStorage.setItem('carboniq_user', JSON.stringify(userWithoutPassword));
      return { success: true };
    }
    
    return { success: false, error: 'Invalid email or password' };
  };

  const signup = (userData) => {
    const users = JSON.parse(localStorage.getItem('carboniq_users') || '[]');
    
    // Check if user already exists
    if (users.some(u => u.email === userData.email)) {
      return { success: false, error: 'Email already registered' };
    }
    
    // Create new user
    const newUser = {
      id: Date.now().toString(),
      ...userData,
      createdAt: new Date().toISOString(),
      organization: userData.organization || 'Not specified'
    };
    
    users.push(newUser);
    localStorage.setItem('carboniq_users', JSON.stringify(users));
    
    // Auto-login after signup
    const { password, ...userWithoutPassword } = newUser;
    setUser(userWithoutPassword);
    localStorage.setItem('carboniq_user', JSON.stringify(userWithoutPassword));
    
    return { success: true };
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('carboniq_user');
  };

  const updateProfile = (updates) => {
    const updatedUser = { ...user, ...updates };
    setUser(updatedUser);
    localStorage.setItem('carboniq_user', JSON.stringify(updatedUser));
    
    // Update in users list
    const users = JSON.parse(localStorage.getItem('carboniq_users') || '[]');
    const userIndex = users.findIndex(u => u.id === user.id);
    if (userIndex !== -1) {
      users[userIndex] = { ...users[userIndex], ...updates };
      localStorage.setItem('carboniq_users', JSON.stringify(users));
    }
  };

  const value = {
    user,
    loading,
    login,
    signup,
    logout,
    updateProfile,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
