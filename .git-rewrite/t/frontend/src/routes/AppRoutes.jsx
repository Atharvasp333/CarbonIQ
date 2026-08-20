import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { ProtectedRoute } from './ProtectedRoute';
import MainLayout from '../layouts/MainLayout';
import Login from '../pages/auth/Login';
import Signup from '../pages/auth/Signup';
import Home from '../pages/main/Home';
import Reports from '../pages/main/Reports';
import Services from '../pages/main/Services';
import ServiceDetail from '../pages/main/ServiceDetail';
import Profile from '../pages/main/Profile';
import Settings from '../pages/main/Settings';
import NotFound from '../pages/NotFound';

export default function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Root - redirect based on auth */}
      <Route 
        path="/" 
        element={isAuthenticated ? <Navigate to="/home" replace /> : <Navigate to="/login" replace />} 
      />

      {/* Auth routes */}
      <Route path="/login" element={isAuthenticated ? <Navigate to="/home" replace /> : <Login />} />
      <Route path="/signup" element={isAuthenticated ? <Navigate to="/home" replace /> : <Signup />} />

      {/* Protected routes with layout */}
      <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route path="/home" element={<Home />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/services" element={<Services />} />
        <Route path="/service/:serviceName" element={<ServiceDetail />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/settings" element={<Settings />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
