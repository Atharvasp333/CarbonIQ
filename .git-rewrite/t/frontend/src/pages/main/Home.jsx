import { useState, useEffect } from 'react';
import { loadDemoData, fetchAWSData, uploadCSV } from '../../api/client';
import Dashboard from '../../components/Dashboard';
import AWSIntegration from '../../components/AWSIntegration';
import ChatBot from '../../components/ChatBot/ChatBot';
import toast from 'react-hot-toast';
import { Upload, FileSpreadsheet } from 'lucide-react';

export default function Home() {
  const [awsData, setAwsData] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showAWSIntegration, setShowAWSIntegration] = useState(!localStorage.getItem('hasLoadedData'));
  const [uploadProgress, setUploadProgress] = useState(false);

  const loadMockDataHandler = async () => {
    setLoading(true);
    try {
      const data = await loadDemoData();
      setAwsData(data);
      // Store data in localStorage for Services and Reports pages
      localStorage.setItem('awsAnalysisData', JSON.stringify(data));
      localStorage.setItem('hasLoadedData', 'true');
      setShowAWSIntegration(false);
      toast.success('Demo data loaded successfully!');
    } catch (error) {
      console.error('Error loading demo data:', error);
      toast.error('Error loading demo data');
    } finally {
      setLoading(false);
    }
  };

  const handleAWSDataLoaded = async (data) => {
    setAwsData(data);
    // Store data in localStorage for Services and Reports pages
    localStorage.setItem('awsAnalysisData', JSON.stringify(data));
    localStorage.setItem('hasLoadedData', 'true');
    setShowAWSIntegration(false);
    toast.success('AWS data loaded successfully!');
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      toast.error('Please upload a CSV file');
      return;
    }

    setUploadProgress(true);
    setLoading(true);
    
    try {
      toast.loading('Processing CSV through agent pipeline...', { id: 'csv-upload' });
      
      const data = await uploadCSV(file);
      
      toast.dismiss('csv-upload');
      
      if (data.success) {
        setAwsData(data);
        // Store complete analysis data in localStorage
        localStorage.setItem('awsAnalysisData', JSON.stringify(data));
        localStorage.setItem('hasLoadedData', 'true');
        setShowAWSIntegration(false);
        toast.success(`✅ CSV processed! ${data.summary.total_emissions_kg.toFixed(2)} kg CO₂ calculated`);
      } else {
        toast.error(data.message || 'Failed to process CSV');
      }
    } catch (error) {
      console.error('Error uploading CSV:', error);
      toast.error('Error processing CSV file');
    } finally {
      setUploadProgress(false);
      setLoading(false);
    }
  };

  const handleBackToIntegration = () => {
    setShowAWSIntegration(true);
  };

  if (showAWSIntegration) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Welcome to CarbonIQ</h1>
          <p className="text-gray-600 mt-2">Connect your AWS account to start analyzing carbon emissions</p>
        </div>

        {/* AWS Integration */}
        <AWSIntegration onDataLoaded={handleAWSDataLoaded} />

        {/* OR Divider */}
        <div className="relative py-4">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-4 bg-gray-50 text-gray-500 font-medium">OR</span>
          </div>
        </div>

        {/* CSV Upload Section */}
        <div className="bg-white rounded-xl p-6 shadow-xl border-2 border-emerald-200">
          <div className="flex items-center mb-4">
            <FileSpreadsheet className="w-6 h-6 text-emerald-600 mr-2" />
            <h2 className="text-2xl font-bold text-gray-800">Upload CUR Report</h2>
          </div>
          
          <p className="text-gray-600 mb-4">
            Upload your AWS Cost and Usage Report (CUR) CSV file for complete analysis through our multi-agent system.
          </p>

          <div className="border-2 border-dashed border-emerald-300 rounded-lg p-8 text-center hover:border-emerald-500 transition-colors">
            <Upload className="w-12 h-12 text-emerald-600 mx-auto mb-4" />
            
            <label htmlFor="csv-upload" className="cursor-pointer">
              <div className="text-lg font-medium text-gray-900 mb-2">
                Click to upload or drag and drop
              </div>
              <div className="text-sm text-gray-500 mb-4">
                AWS CUR Report CSV file (up to 100MB)
              </div>
              <div className="inline-block px-6 py-3 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white font-semibold rounded-lg transition-all shadow-lg hover:shadow-emerald-500/50 transform hover:scale-105">
                Select CSV File
              </div>
            </label>
            
            <input
              id="csv-upload"
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              className="hidden"
              disabled={uploadProgress}
            />
          </div>

          <div className="mt-4 p-4 bg-blue-50 border-2 border-blue-300 rounded-lg">
            <h3 className="text-sm font-semibold text-blue-800 mb-2 flex items-center">
              <svg className="w-4 h-4 mr-2 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              Processing Pipeline
            </h3>
            <p className="text-xs text-blue-700">
              Your CSV will be processed through our 6-agent pipeline: Ingestion → Region Mapping → Carbon Intensity → Emission Calculation → Analytics → Optimization
            </p>
          </div>

          {uploadProgress && (
            <div className="mt-4 p-4 bg-emerald-50 border border-emerald-300 rounded-lg">
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-emerald-600 mr-3"></div>
                <span className="text-emerald-800 font-medium">Processing CSV through agent pipeline...</span>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <>
      <Dashboard
        awsData={awsData}
        insights={insights}
        loading={loading}
        onLoadMock={loadMockDataHandler}
        onBackToIntegration={handleBackToIntegration}
      />
      <ChatBot />
    </>
  );
}
