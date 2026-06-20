import axios from 'axios';
import { getJwtToken } from '../lib/auth';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
});

// Inject JWT on every request
api.interceptors.request.use(async (config) => {
  const token = getJwtToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// On 401 retry once with a fresh token, then reject
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401 && !error.config?._retried) {
      error.config._retried = true;
      const token = getJwtToken();
      if (token) {
        error.config.headers.Authorization = `Bearer ${token}`;
        return api(error.config);
      }
    }
    return Promise.reject(error);
  }
);

// --- Auth -------------------------------------------------------------------

export const authSignup = async ({ name, email, password }) => {
  const res = await api.post('/api/auth/signup', { name, email, password });
  return res.data;
};

export const authLogin = async (email, password) => {
  const res = await api.post('/api/auth/login', { email, password });
  return res.data;
};

export const authMe = async () => {
  const res = await api.get('/api/auth/me');
  return res.data;
};

export const syncUser = async (email, name) => {
  // No auth header needed — syncs Neon Auth user into our users table
  const res = await axios.post(
    `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/auth/sync`,
    { email, name }
  );
  return res.data;
};

// --- AWS Credentials (DB-backed, email-keyed) --------------------------------

const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const saveAWSCredentials = async (creds) => {
  const res = await axios.post(`${BASE}/api/aws/creds/save`, creds);
  return res.data;
};

export const getAWSCredentials = async (email) => {
  const res = await axios.post(`${BASE}/api/aws/creds/get`, { email });
  return res.data;
};

export const deleteAWSCredentials = async (email) => {
  const res = await axios.post(`${BASE}/api/aws/creds/delete`, { email });
  return res.data;
};

export const autoSyncAWS = async () => {
  const res = await api.post('/api/aws/auto-sync', {}, { timeout: 180000 });
  return res.data;
};

// --- Analysis endpoints ------------------------------------------------------

export const uploadCSV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/multi-agent/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  });
  return response.data;
};

export const getMockData = async () => {
  const response = await api.get('/api/mock-data');
  return response.data;
};

export const getInsights = async (data) => {
  const response = await api.post('/api/insights', data);
  return response.data;
};

export const simulateWhatIf = async (scenario) => {
  const response = await api.post('/api/whatif', scenario);
  return response.data;
};

export const checkHealth = async () => {
  const response = await api.get('/api/health');
  return response.data;
};

export const sendChatMessage = async (message) => {
  const response = await api.post('/api/chat', { message });
  return response.data;
};

export const fetchAWSData = async (credentials) => {
  const response = await api.post('/api/aws/fetch', credentials, { timeout: 180000 });
  return response.data;
};

export const loadDemoData = async () => {
  const response = await api.post('/api/multi-agent/analyze-demo', { load_demo: true });
  return response.data;
};

export const getServiceAnalytics = async () => {
  const response = await api.get('/api/service-analytics/summary');
  return response.data;
};

export const getServiceDetail = async (serviceName) => {
  const response = await api.get(`/api/service-analytics/service/${serviceName}`);
  return response.data;
};

export const uploadTimeBasedCSV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/time-based/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const loadTimeBasedDemo = async () => {
  const response = await api.post('/api/time-based/demo');
  return response.data;
};

export default api;

// --- Intelligence Engine endpoints ------------------------------------------------------

export const generateInsights = async () => {
  const response = await api.post('/api/intelligence/generate-insights', {}, { timeout: 120000 });
  return response.data;
};

export const getRecommendations = async () => {
  const response = await api.get('/api/intelligence/recommendations');
  return response.data;
};

export const getRecommendationHistory = async () => {
  const response = await api.get('/api/intelligence/recommendations/history');
  return response.data;
};
