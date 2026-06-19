import { useState, useEffect } from 'react';
import { Save, Building2, Globe, Cpu, Zap, RefreshCw, Target } from 'lucide-react';

export default function OrganizationProfile() {
  const [profile, setProfile] = useState(null);
  const [options, setOptions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const [formData, setFormData] = useState({
    organization_name: '',
    primary_user_region: '',
    workload_type: '',
    latency_sensitivity: '',
    migration_flexibility: '',
    optimization_priority: ''
  });

  useEffect(() => {
    loadProfile();
    loadOptions();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/profile/`);
      if (response.ok) {
        const data = await response.json();
        if (data) {
          setProfile(data);
          setFormData(data);
        }
      }
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadOptions = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/profile/options`);
      if (response.ok) {
        const data = await response.json();
        setOptions(data);
      }
    } catch (error) {
      console.error('Failed to load options:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/profile/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
        setMessage('Profile saved successfully!');
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage('Failed to save profile');
      }
    } catch (error) {
      console.error('Failed to save profile:', error);
      setMessage('Error saving profile');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-gray-600">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Organization Profile</h1>
          <p className="text-gray-600">
            Configure your organization's sustainability preferences to receive personalized recommendations.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
          {/* Organization Name */}
          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
              <Building2 className="w-4 h-4" />
              Organization Name
            </label>
            <input
              type="text"
              required
              value={formData.organization_name}
              onChange={(e) => handleChange('organization_name', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Enter your organization name"
            />
          </div>

          {/* Primary User Region */}
          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
              <Globe className="w-4 h-4" />
              Primary User Region
            </label>
            <select
              required
              value={formData.primary_user_region}
              onChange={(e) => handleChange('primary_user_region', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Select region...</option>
              {options?.primary_user_region?.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">Where are your primary users located?</p>
          </div>

          {/* Workload Type */}
          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
              <Cpu className="w-4 h-4" />
              Workload Type
            </label>
            <select
              required
              value={formData.workload_type}
              onChange={(e) => handleChange('workload_type', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Select workload type...</option>
              {options?.workload_type?.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">What type of workload do you run?</p>
          </div>

          {/* Latency Sensitivity */}
          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
              <Zap className="w-4 h-4" />
              Latency Sensitivity
            </label>
            <select
              required
              value={formData.latency_sensitivity}
              onChange={(e) => handleChange('latency_sensitivity', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Select sensitivity...</option>
              {options?.latency_sensitivity?.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">How sensitive is your application to latency?</p>
          </div>

          {/* Migration Flexibility */}
          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
              <RefreshCw className="w-4 h-4" />
              Migration Flexibility
            </label>
            <select
              required
              value={formData.migration_flexibility}
              onChange={(e) => handleChange('migration_flexibility', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Select flexibility...</option>
              {options?.migration_flexibility?.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">Can you migrate workloads across regions?</p>
          </div>

          {/* Optimization Priority */}
          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-gray-700 mb-2">
              <Target className="w-4 h-4" />
              Optimization Priority
            </label>
            <select
              required
              value={formData.optimization_priority}
              onChange={(e) => handleChange('optimization_priority', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Select priority...</option>
              {options?.optimization_priority?.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">What is your primary optimization goal?</p>
          </div>

          {/* Submit Button */}
          <div className="flex items-center justify-between pt-4">
            <div>
              {message && (
                <p className={`text-sm ${message.includes('success') ? 'text-green-600' : 'text-red-600'}`}>
                  {message}
                </p>
              )}
            </div>
            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-600 to-blue-600 text-white font-semibold rounded-lg hover:from-green-700 hover:to-blue-700 transition disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              {saving ? 'Saving...' : 'Save Profile'}
            </button>
          </div>
        </form>

        {/* Info Box */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">Why configure your profile?</h3>
          <p className="text-sm text-blue-800">
            Your profile helps CarbonIQ generate personalized sustainability recommendations that respect your 
            constraints. Recommendations are validated against your latency requirements, migration flexibility, 
            and optimization priorities to ensure they're actionable for your organization.
          </p>
        </div>
      </div>
    </div>
  );
}
