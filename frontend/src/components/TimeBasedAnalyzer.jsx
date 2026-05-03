import { useState } from 'react';
import { uploadTimeBasedCSV, loadTimeBasedDemo } from '../api/client';
import TimeBasedDashboard from './TimeBasedDashboard';

function TimeBasedAnalyzer() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.csv')) {
        setError('Please select a CSV file');
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await uploadTimeBasedCSV(file);
      setData(result);
    } catch (err) {
      setError(err.message || 'Failed to process CSV');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadDemo = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await loadTimeBasedDemo();
      setData(result);
    } catch (err) {
      setError(err.message || 'Failed to load demo data');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setData(null);
    setFile(null);
    setError(null);
  };

  if (data) {
    return <TimeBasedDashboard data={data} onBack={handleBack} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-white">AWS CSV Analyzer</h1>
          <p className="text-slate-400 text-sm">Time-Based Carbon Emission Analysis with Electricity Maps</p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
          <h2 className="text-2xl font-bold text-white mb-6">Upload AWS CSV Data</h2>
          
          <div className="space-y-6">
            {/* File Upload Section */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Select CSV File
              </label>
              <div className="flex gap-4">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="flex-1 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleUpload}
                  disabled={loading || !file}
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-medium rounded-lg transition"
                >
                  {loading ? 'Processing...' : 'Analyze'}
                </button>
              </div>
              {file && (
                <p className="mt-2 text-sm text-slate-400">
                  Selected: {file.name}
                </p>
              )}
            </div>

            {/* Divider */}
            <div className="flex items-center gap-4">
              <div className="flex-1 h-px bg-slate-600"></div>
              <span className="text-slate-400 text-sm">OR</span>
              <div className="flex-1 h-px bg-slate-600"></div>
            </div>

            {/* Demo Data Button */}
            <div>
              <button
                onClick={handleLoadDemo}
                disabled={loading}
                className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-slate-600 text-white font-medium rounded-lg transition"
              >
                {loading ? 'Loading...' : 'Load Demo Data'}
              </button>
              <p className="mt-2 text-sm text-slate-400 text-center">
                Try with sample AWS billing data
              </p>
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-500/10 border border-red-500 rounded-lg p-4">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            {/* Info Box */}
            <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
              <h3 className="text-sm font-semibold text-blue-400 mb-2">ℹ️ How It Works</h3>
              <ul className="text-xs text-slate-300 space-y-1">
                <li>• Upload AWS Cost and Usage Report (CUR) CSV file</li>
                <li>• System extracts timestamps from each row</li>
                <li>• Fetches historical carbon intensity from Electricity Maps API</li>
                <li>• Calculates time-accurate carbon emissions</li>
                <li>• Displays emissions by service, region, and time</li>
              </ul>
            </div>

            {/* Expected Format */}
            <div className="mt-4 p-4 bg-slate-700/50 rounded-lg">
              <h3 className="text-sm font-semibold text-slate-300 mb-2">📋 Expected CSV Format</h3>
              <div className="text-xs text-slate-400 font-mono">
                <p>Required columns:</p>
                <ul className="mt-2 space-y-1">
                  <li>• product/ProductName or Service</li>
                  <li>• product/region or Region</li>
                  <li>• lineItem/UsageAmount or UsageAmount</li>
                  <li>• lineItem/UsageStartDate or Timestamp</li>
                  <li>• lineItem/UnblendedCost or Cost (optional)</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default TimeBasedAnalyzer;
