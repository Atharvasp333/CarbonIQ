import { useState } from 'react';
import { loadDemoData, uploadCSV } from '../../api/client';
import ChatBot from '../../components/ChatBot/ChatBot';
import AWSConnectBanner from '../../components/AWSConnectBanner';
import toast from 'react-hot-toast';
import { Upload, FileSpreadsheet, CheckCircle, BarChart3, Server, ArrowRight, Lightbulb } from 'lucide-react';
import { Link } from 'react-router-dom';

function loadSavedSummary() {
  try {
    const raw = localStorage.getItem('awsAnalysisData');
    if (!raw) return null;
    const data = JSON.parse(raw);
    return data?.summary ?? null;
  } catch {
    return null;
  }
}

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(false);
  const [dataUploaded, setDataUploaded] = useState(!!localStorage.getItem('hasLoadedData'));
  const [lastUploadSummary, setLastUploadSummary] = useState(() => loadSavedSummary());

  const loadMockDataHandler = async () => {
    setLoading(true);
    try {
      const data = await loadDemoData();
      // Store data in localStorage for Services and Reports pages
      localStorage.setItem('awsAnalysisData', JSON.stringify(data));
      localStorage.setItem('hasLoadedData', 'true');
      setDataUploaded(true);
      setLastUploadSummary(data.summary);
      toast.success('Demo data loaded successfully!');
    } catch (error) {
      console.error('Error loading demo data:', error);
      toast.error('Error loading demo data');
    } finally {
      setLoading(false);
    }
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
        // Store complete analysis data in localStorage
        localStorage.setItem('awsAnalysisData', JSON.stringify(data));
        localStorage.setItem('hasLoadedData', 'true');
        setDataUploaded(true);
        setLastUploadSummary(data.summary);
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

  const handleUploadAnother = () => {
    // Clear file input
    const fileInput = document.getElementById('csv-upload');
    if (fileInput) fileInput.value = '';
  };

  const handleAutoSyncData = (data) => {
    if (data?.summary) {
      localStorage.setItem('awsAnalysisData', JSON.stringify(data));
      localStorage.setItem('hasLoadedData', 'true');
      setDataUploaded(true);
      setLastUploadSummary(data.summary);
    }
  };

  return (
    <>
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Welcome to CarbonIQ</h1>
          <p className="text-gray-600 mt-2">Upload your AWS Cost and Usage Report to analyze carbon emissions</p>
        </div>

        {/* AWS Connect Banner */}
        <AWSConnectBanner onDataLoaded={handleAutoSyncData} />

        {/* Success Message - Show after data is uploaded */}
        {dataUploaded && lastUploadSummary && (
          <div className="bg-gradient-to-r from-emerald-50 to-green-50 border-2 border-emerald-300 rounded-xl p-6 shadow-lg">
            <div className="flex items-start">
              <CheckCircle className="w-8 h-8 text-emerald-600 mr-4 flex-shrink-0 mt-1" />
              <div className="flex-grow">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">✅ Data Processed Successfully!</h2>
                <p className="text-gray-700 mb-4">
                  Your AWS data has been analyzed through our 6-agent pipeline. View detailed insights in the tabs below.
                </p>
                
                {/* Summary Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-white rounded-lg p-4 border border-emerald-200">
                    <p className="text-sm text-gray-600 mb-1">Total Emissions</p>
                    <p className="text-2xl font-bold text-red-600">{lastUploadSummary.total_emissions_kg?.toFixed(2)} kg CO₂</p>
                  </div>
                  <div className="bg-white rounded-lg p-4 border border-emerald-200">
                    <p className="text-sm text-gray-600 mb-1">Total Cost</p>
                    <p className="text-2xl font-bold text-blue-600">${lastUploadSummary.total_cost?.toFixed(2)}</p>
                  </div>
                  <div className="bg-white rounded-lg p-4 border border-emerald-200">
                    <p className="text-sm text-gray-600 mb-1">Energy Used</p>
                    <p className="text-2xl font-bold text-purple-600">{lastUploadSummary.total_energy_kwh?.toFixed(2)} kWh</p>
                  </div>
                </div>

                {/* Navigation Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Link
                    to="/insights"
                    className="group bg-white hover:bg-green-50 border-2 border-green-300 hover:border-green-500 rounded-lg p-5 transition-all flex items-center justify-between"
                  >
                    <div className="flex items-center">
                      <div className="bg-green-100 p-3 rounded-lg mr-4">
                        <Lightbulb className="w-6 h-6 text-green-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-gray-900 group-hover:text-green-700">Insights</h3>
                        <p className="text-sm text-gray-600">AI-powered sustainability recommendations</p>
                      </div>
                    </div>
                    <ArrowRight className="w-5 h-5 text-green-600 group-hover:translate-x-1 transition-transform" />
                  </Link>

                  <Link
                    to="/services"
                    className="group bg-white hover:bg-emerald-50 border-2 border-emerald-300 hover:border-emerald-500 rounded-lg p-5 transition-all flex items-center justify-between"
                  >
                    <div className="flex items-center">
                      <div className="bg-emerald-100 p-3 rounded-lg mr-4">
                        <Server className="w-6 h-6 text-emerald-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-gray-900 group-hover:text-emerald-700">Services</h3>
                        <p className="text-sm text-gray-600">View service breakdown & regional analysis</p>
                      </div>
                    </div>
                    <ArrowRight className="w-5 h-5 text-emerald-600 group-hover:translate-x-1 transition-transform" />
                  </Link>

                  <Link
                    to="/reports"
                    className="group bg-white hover:bg-blue-50 border-2 border-blue-300 hover:border-blue-500 rounded-lg p-5 transition-all flex items-center justify-between"
                  >
                    <div className="flex items-center">
                      <div className="bg-blue-100 p-3 rounded-lg mr-4">
                        <BarChart3 className="w-6 h-6 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-gray-900 group-hover:text-blue-700">Reports</h3>
                        <p className="text-sm text-gray-600">Detailed analytics & time-based trends</p>
                      </div>
                    </div>
                    <ArrowRight className="w-5 h-5 text-blue-600 group-hover:translate-x-1 transition-transform" />
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* CSV Upload Section */}
        <div className="bg-white rounded-xl p-6 shadow-xl border-2 border-gray-200">
          <div className="flex items-center mb-4">
            <FileSpreadsheet className="w-6 h-6 text-emerald-600 mr-2" />
            <h2 className="text-2xl font-bold text-gray-800">
              {dataUploaded ? 'Upload Another CUR Report' : 'Upload CUR Report'}
            </h2>
          </div>
          
          <p className="text-gray-600 mb-4">
            Upload your AWS Cost and Usage Report (CUR) CSV file for complete analysis through our multi-agent system.
          </p>

          <div className="border-2 border-dashed border-gray-300 hover:border-emerald-500 rounded-lg p-8 text-center transition-colors">
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            
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
              onClick={handleUploadAnother}
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

        {/* Demo Data Button */}
        {!dataUploaded && (
          <div className="text-center">
            <button
              onClick={loadMockDataHandler}
              disabled={loading}
              className="px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold rounded-lg transition-all border-2 border-gray-300"
            >
              {loading ? 'Loading...' : 'Or Load Demo Data'}
            </button>
          </div>
        )}
      </div>
      <ChatBot />
    </>
  );
}
