import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
});

// Inject JWT token on every request (kept for compatibility if backend needs it)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('carboniq_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirect to login on 401
api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// --- Auth (kept for backward compat, prefer authClient from lib/auth.js) ----

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

// --- Existing endpoints ------------------------------------------------------

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
  const response = await api.post('/api/aws/fetch', credentials);
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
