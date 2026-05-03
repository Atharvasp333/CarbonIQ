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
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
      <h2 className="text-2xl font-bold text-white mb-6">AWS Data Integration</h2>
      
      <form onSubmit={handleFetchAWS} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              AWS Access Key
            </label>
            <input
              type="text"
              name="access_key"
              value={formData.access_key}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="AKIAIOSFODNN7EXAMPLE"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              AWS Secret Key
            </label>
            <input
              type="password"
              name="secret_key"
              value={formData.secret_key}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              AWS Region
            </label>
            <select
              name="region"
              value={formData.region}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
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
            <label className="block text-sm font-medium text-slate-300 mb-2">
              S3 Bucket Name
            </label>
            <input
              type="text"
              name="bucket_name"
              value={formData.bucket_name}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="my-cur-bucket"
              required
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-300 mb-2">
              S3 File Path (Optional - will fetch latest if empty)
            </label>
            <input
              type="text"
              name="file_key"
              value={formData.file_key}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="cur-reports/2024/01/report.csv"
            />
          </div>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500 rounded-lg p-4">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-medium py-3 px-6 rounded-lg transition"
          >
            {loading ? 'Fetching...' : 'Fetch AWS Data'}
          </button>

          <button
            type="button"
            onClick={handleLoadDemo}
            disabled={loading}
            className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-slate-600 text-white font-medium py-3 px-6 rounded-lg transition"
          >
            {loading ? 'Loading...' : 'Load Demo Data'}
          </button>
        </div>
      </form>

      <div className="mt-6 p-4 bg-slate-700/50 rounded-lg">
        <h3 className="text-sm font-semibold text-slate-300 mb-2">ℹ️ Security Note</h3>
        <p className="text-xs text-slate-400">
          Your AWS credentials are processed in-memory and never stored. 
          Ensure your IAM user has S3 read permissions for the specified bucket.
        </p>
      </div>
    </div>
  );
}

export default AWSIntegration;
