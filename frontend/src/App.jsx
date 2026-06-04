import { useState, useEffect } from 'react';
import { uploadCSV, getMockData, getInsights, fetchAWSData, loadDemoData } from './api/client';
import Dashboard from './components/Dashboard';
import ChatBot from './components/ChatBot/ChatBot';
import AWSIntegration from './components/AWSIntegration';
import MultiAgentDashboard from './components/MultiAgentDashboard';

function App() {
  const [awsData, setAwsData] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showAWSIntegration, setShowAWSIntegration] = useState(true);
  const [view, setView] = useState('classic'); // 'classic' or 'multi-agent'

  useEffect(() => {
    // Don't auto-load mock data, let user choose
  }, []);

  const loadMockDataHandler = async () => {
    setLoading(true);
    try {
      const data = await loadDemoData();
      setAwsData(data);
      await fetchInsights(data);
      setShowAWSIntegration(false);
    } catch (error) {
      console.error('Error loading demo data:', error);
      alert('Error loading demo data');
    } finally {
      setLoading(false);
    }
  };

  const handleAWSDataLoaded = async (data) => {
    setAwsData(data);
    await fetchInsights(data);
    setShowAWSIntegration(false);
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

  const handleBackToIntegration = () => {
    setShowAWSIntegration(true);
  };

  // Render Multi-Agent Dashboard
  if (view === 'multi-agent') {
    return (
      <div className="relative">
        <button
          onClick={() => setView('classic')}
          className="absolute top-4 left-4 z-50 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg backdrop-blur-sm border border-white/20 transition-all"
        >
          ← Back to Classic View
        </button>
        <MultiAgentDashboard />
      </div>
    );
  }

  return (
    <>
      {showAWSIntegration ? (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
          <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700">
            <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold text-white">CarbonIQ Cloud Analyzer</h1>
                <p className="text-slate-400 text-sm">AWS Billing → Carbon Intelligence</p>
              </div>
              <button
                onClick={() => setView('multi-agent')}
                className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-lg font-semibold transition-all transform hover:scale-105"
              >
                🤖 Multi-Agent Dashboard
              </button>
            </div>
          </header>
          <main className="max-w-4xl mx-auto px-6 py-8">
            <AWSIntegration onDataLoaded={handleAWSDataLoaded} />
          </main>
        </div>
      ) : (
        <>
          <Dashboard
            awsData={awsData}
            insights={insights}
            loading={loading}
            onUpload={handleUpload}
            onLoadMock={loadMockDataHandler}
            onBackToIntegration={handleBackToIntegration}
          />
          <ChatBot />
        </>
      )}
    </>
  );
}

export default App;
