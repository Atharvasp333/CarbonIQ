import { useState, useEffect } from 'react';
import { Bell, Moon, Zap, Trash2, Building2, Globe, Cpu, RefreshCw, Target } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Settings() {
  const [settings, setSettings] = useState({
    darkMode: false,
    notifications: true,
    units: 'metric',
    refreshInterval: '5',
    theme: 'light'
  });

  const [orgProfile, setOrgProfile] = useState(null);
  const [profileOptions, setProfileOptions] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileForm, setProfileForm] = useState({
    organization_name: '',
    primary_user_region: '',
    workload_type: '',
    latency_sensitivity: '',
    migration_flexibility: '',
    optimization_priority: ''
  });

  useEffect(() => {
    loadOrgProfile();
    loadProfileOptions();
  }, []);

  const loadOrgProfile = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/profile/`);
      if (response.ok) {
        const data = await response.json();
        if (data) {
          setOrgProfile(data);
          setProfileForm(data);
        }
      }
    } catch (error) {
      console.error('Failed to load organization profile:', error);
    } finally {
      setProfileLoading(false);
    }
  };

  const loadProfileOptions = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/profile/options`);
      if (response.ok) {
        const data = await response.json();
        setProfileOptions(data);
        console.log('Loaded profile options:', data);
      } else {
        console.error('Failed to fetch options, using fallback');
        setProfileOptions(getFallbackOptions());
      }
    } catch (error) {
      console.error('Failed to load profile options:', error);
      // Use fallback options if API fails
      setProfileOptions(getFallbackOptions());
    }
  };

  const getFallbackOptions = () => ({
    primary_user_region: [
      "India",
      "North America",
      "Europe",
      "Asia Pacific",
      "Global"
    ],
    workload_type: [
      "Production",
      "Development",
      "Testing",
      "Analytics",
      "Machine Learning",
      "Mixed"
    ],
    latency_sensitivity: [
      "High",
      "Medium",
      "Low"
    ],
    migration_flexibility: [
      "Yes",
      "Some Workloads",
      "No"
    ],
    optimization_priority: [
      "Reduce Carbon",
      "Reduce Cost",
      "Balance Both"
    ]
  });

  const saveOrgProfile = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/profile/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileForm)
      });

      if (response.ok) {
        const data = await response.json();
        setOrgProfile(data);
        toast.success('Organization profile saved successfully!');
      } else {
        toast.error('Failed to save organization profile');
      }
    } catch (error) {
      console.error('Failed to save profile:', error);
      toast.error('Error saving organization profile');
    }
  };

  const handleProfileChange = (field, value) => {
    setProfileForm(prev => ({ ...prev, [field]: value }));
  };

  const handleToggle = (key) => {
    setSettings(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
    toast.success('Settings updated');
  };

  const handleChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
    toast.success('Settings updated');
  };

  const handleDeleteAccount = () => {
    if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      toast.error('Account deletion is not available in demo mode');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">Manage your application preferences</p>
      </div>

      {/* Preferences Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Preferences</h2>
        </div>
        <div className="p-6 space-y-6">
          {/* Dark Mode */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Moon className="text-gray-600" size={20} />
              <div>
                <p className="font-medium text-gray-900">Dark Mode</p>
                <p className="text-sm text-gray-600">Use dark theme throughout the application</p>
              </div>
            </div>
            <button
              onClick={() => handleToggle('darkMode')}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                settings.darkMode ? 'bg-[#2D6A4F]' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  settings.darkMode ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Notifications */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Bell className="text-gray-600" size={20} />
              <div>
                <p className="font-medium text-gray-900">Notifications</p>
                <p className="text-sm text-gray-600">Receive alerts about carbon intensity changes</p>
              </div>
            </div>
            <button
              onClick={() => handleToggle('notifications')}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                settings.notifications ? 'bg-[#2D6A4F]' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  settings.notifications ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      {/* Application Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Application</h2>
        </div>
        <div className="p-6 space-y-6">
          {/* Data Refresh Interval */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data Refresh Interval
            </label>
            <select
              value={settings.refreshInterval}
              onChange={(e) => handleChange('refreshInterval', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#40916C] focus:border-transparent"
            >
              <option value="1">Every 1 minute</option>
              <option value="5">Every 5 minutes</option>
              <option value="10">Every 10 minutes</option>
              <option value="30">Every 30 minutes</option>
              <option value="60">Every hour</option>
            </select>
          </div>
        </div>
      </div>

      {/* Organization Profile Section (NEW) */}
      <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-xl shadow-sm border border-green-200">
        <div className="p-6 border-b border-green-200">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Building2 className="text-green-600" size={24} />
            Organization Profile
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Configure sustainability preferences for personalized recommendations
          </p>
        </div>
        
        {profileLoading ? (
          <div className="p-6 text-center text-gray-600">Loading profile...</div>
        ) : (
          <div className="p-6 space-y-4">
            {/* Debug info - remove in production */}
            {!profileOptions && (
              <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  ⚠️ Backend API not responding. Using default options. Start backend with: <code className="font-mono bg-yellow-100 px-2 py-1 rounded">python -m uvicorn main:app --reload --port 8000</code>
                </p>
              </div>
            )}
            
            {/* Organization Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Organization Name
              </label>
              <input
                type="text"
                value={profileForm.organization_name}
                onChange={(e) => handleProfileChange('organization_name', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Enter your organization name"
              />
            </div>

            {/* Primary User Region */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <Globe size={16} />
                Primary User Region
              </label>
              <select
                value={profileForm.primary_user_region}
                onChange={(e) => handleProfileChange('primary_user_region', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="">Select region...</option>
                {profileOptions?.primary_user_region?.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>

            {/* Workload Type */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <Cpu size={16} />
                Workload Type
              </label>
              <select
                value={profileForm.workload_type}
                onChange={(e) => handleProfileChange('workload_type', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="">Select workload type...</option>
                {profileOptions?.workload_type?.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>

            {/* Latency Sensitivity */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <Zap size={16} />
                Latency Sensitivity
              </label>
              <select
                value={profileForm.latency_sensitivity}
                onChange={(e) => handleProfileChange('latency_sensitivity', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="">Select sensitivity...</option>
                {profileOptions?.latency_sensitivity?.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>

            {/* Migration Flexibility */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <RefreshCw size={16} />
                Migration Flexibility
              </label>
              <select
                value={profileForm.migration_flexibility}
                onChange={(e) => handleProfileChange('migration_flexibility', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="">Select flexibility...</option>
                {profileOptions?.migration_flexibility?.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>

            {/* Optimization Priority */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <Target size={16} />
                Optimization Priority
              </label>
              <select
                value={profileForm.optimization_priority}
                onChange={(e) => handleProfileChange('optimization_priority', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="">Select priority...</option>
                {profileOptions?.optimization_priority?.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>

            {/* Save Button */}
            <div className="pt-4">
              <button
                onClick={saveOrgProfile}
                className="w-full px-6 py-3 bg-gradient-to-r from-green-600 to-blue-600 text-white font-semibold rounded-lg hover:from-green-700 hover:to-blue-700 transition"
              >
                Save Organization Profile
              </button>
            </div>

            {/* Info */}
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                💡 Your profile helps CarbonIQ generate personalized sustainability recommendations 
                that respect your constraints and priorities.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Account Section */}
      <div className="bg-white rounded-xl shadow-sm border border-red-200">
        <div className="p-6 border-b border-red-200">
          <h2 className="text-xl font-bold text-red-900">Danger Zone</h2>
        </div>
        <div className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Delete Account</p>
              <p className="text-sm text-gray-600 mt-1">
                Permanently delete your account and all associated data
              </p>
            </div>
            <button
              onClick={handleDeleteAccount}
              className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              <Trash2 size={18} className="mr-2" />
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
