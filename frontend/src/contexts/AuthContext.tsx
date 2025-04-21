import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (name: string, email: string, password: string) => Promise<User>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = () => {
      const authStatus = authService.isAuthenticated();
      setIsAuthenticated(authStatus);
      
      // If authenticated, you might want to fetch user data here
      // For now, we'll just use the stored userId
      if (authStatus) {
        const userId = localStorage.getItem('userId');
        if (userId && userId !== 'undefined') {
          setUser({ id: userId, name: '', email: '', created_at: '' });
        }
      }
      
      setLoading(false);
    };
    
    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const userData = await authService.login(email, password);
      setUser(userData);
      setIsAuthenticated(true);
      localStorage.setItem('userId', userData.id);
      return userData;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (name: string, email: string, password: string) => {
    try {
      const userData = await authService.register(name, email, password);
      setUser(userData);
      setIsAuthenticated(true);
      localStorage.setItem('userId', userData.id);
      return userData;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('userId');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
