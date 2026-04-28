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

export const simulateCloudUsage = async (data) => {
  const response = await api.post('/api/simulate', data);
  return response.data;
};

export const uploadCustomCSV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/upload-custom-csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

export const getResultsHistory = async () => {
  const response = await api.get('/api/results');
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
