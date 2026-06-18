import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

export const uploadCSV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/multi-agent/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000 // 2 minutes timeout for large CSV processing
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
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const loadTimeBasedDemo = async () => {
  const response = await api.post('/api/time-based/demo');
  return response.data;
};
