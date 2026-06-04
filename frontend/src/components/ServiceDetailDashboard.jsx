import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Activity, DollarSign, Zap, TrendingUp, Clock, 
  MapPin, AlertTriangle, Lightbulb, BarChart3 
} from 'lucide-react';
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000'
});

const ServiceDetailDashboard = () => {
  const { serviceName } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadServiceAnalytics();
  }, [serviceName]);

  const loadServiceAnalytics = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get(`/api/service-analytics/${serviceName}`);
      setAnalytics(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load service analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent"></div>
          <p className="text-white mt-4 text-xl">Loading {serviceName} analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 p-8">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => navigate('/')}
            className="mb-4 flex items-center gap-2 text-white hover:text-blue-300"
          >
            <ArrowLeft size={20} />
            Back to Dashboard
          </button>
          <div className="bg-red-500/20 border border-red-500 rounded-xl p-6 text-center">
            <AlertTriangle className="mx-auto mb-4 text-red-400" size={48} />
            <h3 className="text-2xl font-bold text-white mb-2">Error Loading Analytics</h3>
            <p className="text-red-200">{error}</p>
            <button
              onClick={() => navigate('/')}
              className="mt-6 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!analytics) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        
        {/* Breadcrumb */}
        <div className="mb-6 flex items-center gap-2 text-gray-400">
          <button
            onClick={() => navigate('/')}
            className="hover:text-white transition-colors"
          >
            Dashboard
          </button>
          <span>›</span>
          <span className="text-white font-semibold">{analytics.service_name}</span>
        <