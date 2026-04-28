import { useState, useEffect } from 'react';
import { uploadCSV, getMockData, getInsights } from './api/client';
import Dashboard from './components/Dashboard';
import ChatBot from './components/ChatBot/ChatBot';

function App() {
  const [awsData, setAwsData] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadMockData();
  }, []);

  const loadMockData = async () => {
    setLoading(true);
    try {
      const data = await getMockData();
      setAwsData(data);
      await fetchInsights(data);
    } catch (error) {
      console.error('Error loading mock data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file) => {
    setLoading(true);
    try {
      const data = await uploadCSV(file);
      setAwsData(data);
      await fetchInsights(data);
    } catch (error) {
      console.error('Error uploading CSV:', error);
      alert('Error uploading CSV. Please check the file format.');
    } finally {
      setLoading(false);
    }
  };

  const fetchInsights = async (data) => {
    try {
      const insightsData = await getInsights({
        total_co2_kg: data.total_co2_kg,
        total_cost: data.total_cost,
        top_region: data.top_region,
        top_service: data.top_service,
        by_service: data.by_service,
        by_region: data.by_region
      });
      setInsights(insightsData);
    } catch (error) {
      console.error('Error fetching insights:', error);
    }
  };

  return (
    <>
      <Dashboard
        awsData={awsData}
        insights={insights}
        loading={loading}
        onUpload={handleUpload}
        onLoadMock={loadMockData}
      />
      <ChatBot />
    </>
  );
}

export default App;
