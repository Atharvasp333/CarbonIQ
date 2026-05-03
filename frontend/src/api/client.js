import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

export const uploadCSV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/upload-csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
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
  const response = await api.post('/api/aws/demo');
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
