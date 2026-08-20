import { useState } from 'react';
import { fetchAWSData, loadDemoData } from '../api/client';

function AWSIntegration({ onDataLoaded }) {
  const [formData, setFormData] = useState({
    access_key: '',
    secret_key: '',
    region: 'us-east-1',
    bucket_name: '',
    file_key: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleFetchAWS = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await fetchAWSData(formData);
      onDataLoaded(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch AWS data');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadDemo = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await loadDemoData();
      onDataLoaded(data);
    } catch (err) {
      setError(err.message || 'Failed to load demo data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl p-6 shadow-xl border-2 border-emerald-200">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">AWS Data Integration</h2>
      
      <form onSubmit={handleFetchAWS} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AWS Access Key
            </label>
            <input
              type="text"
              name="access_key"
              value={formData.access_key}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-emerald-50 border-2 border-emerald-200 rounded-lg text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
              placeholder="AKIAIOSFODNN7EXAMPLE"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AWS Secret Key
            </label>
            <input
              type="password"
              name="secret_key"
              value={formData.secret_key}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-emerald-50 border-2 border-emerald-200 rounded-lg text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
              placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AWS Region
            </label>
            <select
              name="region"
              value={formData.region}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-emerald-50 border-2 border-emerald-200 rounded-lg text-gray-800 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
            >
              <option value="us-east-1">US East (N. Virginia)</option>
              <option value="us-east-2">US East (Ohio)</option>
              <option value="us-west-1">US West (N. California)</option>
              <option value="us-west-2">US West (Oregon)</option>
              <option value="eu-west-1">EU (Ireland)</option>
              <option value="eu-central-1">EU (Frankfurt)</option>
              <option value="ap-south-1">Asia Pacific (Mumbai)</option>
              <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
              <option value="ap-northeast-1">Asia Pacific (Tokyo)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              S3 Bucket Name
            </label>
            <input
              type="text"
              name="bucket_name"
              value={formData.bucket_name}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-emerald-50 border-2 border-emerald-200 rounded-lg text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
              placeholder="my-cur-bucket"
              required
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              S3 File Path (Optional - will fetch latest if empty)
            </label>
            <input
              type="text"
              name="file_key"
              value={formData.file_key}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-emerald-50 border-2 border-emerald-200 rounded-lg text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
              placeholder="reports/CUR_report/ or full path"
            />
            <p className="text-xs text-gray-500 mt-1">
              Supports .csv and .csv.gz files. Leave empty to auto-fetch the latest file.
            </p>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
            <p className="text-red-700 text-sm font-medium">{error}</p>
          </div>
        )}

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold py-3 px-6 rounded-lg transition-all shadow-lg hover:shadow-emerald-500/50 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]"
          >
            {loading ? 'Fetching...' : 'Fetch AWS Data'}
          </button>

          <button
            type="button"
            onClick={handleLoadDemo}
            disabled={loading}
            className="flex-1 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-700 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold py-3 px-6 rounded-lg transition-all shadow-lg hover:shadow-teal-500/50 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]"
          >
            {loading ? 'Loading...' : 'Load Demo Data'}
          </button>
        </div>
      </form>

      <div className="mt-6 p-4 bg-emerald-50 border-2 border-emerald-300 rounded-lg">
        <h3 className="text-sm font-semibold text-emerald-800 mb-2 flex items-center">
          <svg className="w-4 h-4 mr-2 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          Security Note
        </h3>
        <p className="text-xs text-emerald-700">
          Your AWS credentials are processed in-memory and never stored. 
          Ensure your IAM user has S3 read permissions for the specified bucket.
        </p>
      </div>
    </div>
  );
}

export default AWSIntegration;
