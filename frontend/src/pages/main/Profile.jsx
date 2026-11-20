import { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { User, Mail, Building, Calendar, Edit2, Save, X, Lock, CheckCircle2, AlertCircle, BarChart3, ShieldCheck, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Profile() {
  const { user, loading: authLoading, updateProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [validationError, setValidationError] = useState('');
  
  const [formData, setFormData] = useState({
    name: '',
    organization: ''
  });

  // Sync form data with authenticated user
  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        organization: user.organization || ''
      });
    }
  }, [user]);

  // Read real user audit metrics if an analysis has been executed
  const [auditStats, setAuditStats] = useState(null);
  useEffect(() => {
    try {
      const stored = localStorage.getItem('awsAnalysisData');
      if (stored) {
        const parsed = JSON.parse(stored);
        const norm = parsed?.results || parsed;
        if (norm?.summary) {
          setAuditStats({
            totalEmissionsKg: norm.summary.total_emissions_kg,
            totalEnergyKwh: norm.summary.total_energy_kwh,
            topService: norm.summary.top_service,
            topRegion: norm.summary.top_region,
            analyzedAt: norm.summary.analyzed_at || parsed.uploaded_at
          });
        }
      }
    } catch (_) {}
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setValidationError('');

    const trimmedName = formData.name.trim();
    if (!trimmedName) {
      setValidationError('Full name is required.');
      toast.error('Full name cannot be empty');
      return;
    }

    setSaving(true);
    try {
      const res = await updateProfile({
        name: trimmedName,
        organization: formData.organization.trim()
      });

      if (res?.success) {
        toast.success('Profile saved to database successfully!');
        setIsEditing(false);
      } else {
        toast.error(res?.error || 'Failed to update profile');
      }
    } catch (err) {
      console.error('Profile update error:', err);
      toast.error('An unexpected error occurred while saving profile');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      name: user?.name || '',
      organization: user?.organization || ''
    });
    setValidationError('');
    setIsEditing(false);
  };

  if (authLoading) {
    return (
      <div className="max-w-4xl mx-auto py-12 text-center">
        <Loader2 className="w-8 h-8 text-[#2D6A4F] animate-spin mx-auto mb-3" />
        <p className="text-gray-600 font-medium">Loading user profile from database...</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="max-w-4xl mx-auto py-12 text-center bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <AlertCircle className="w-12 h-12 text-yellow-500 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-gray-900 mb-2">No Active Account Session</h2>
        <p className="text-gray-600 mb-4">Please log in to manage your sustainability profile.</p>
        <a
          href="/login"
          className="inline-flex items-center px-4 py-2 bg-[#2D6A4F] text-white rounded-lg hover:bg-[#1B4332] font-semibold text-sm transition"
        >
          Go to Login
        </a>
      </div>
    );
  }

  const memberSinceStr = user.createdAt
    ? new Date(user.createdAt).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    : 'Active Account';

  const userInitial = user.name ? user.name.charAt(0).toUpperCase() : 'U';

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">User Profile</h1>
          <p className="text-gray-600 mt-1">Manage your account identity, organization affiliation, and audit access.</p>
        </div>
        <div className="flex items-center gap-2 text-xs font-semibold px-3 py-1.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-full w-fit">
          <ShieldCheck size={14} className="text-emerald-600" />
          <span>JWT Authenticated Session</span>
        </div>
      </div>

      {/* Profile Card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {/* Header Section */}
        <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-emerald-50/50 to-transparent">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-[#2D6A4F] text-white rounded-full flex items-center justify-center font-bold text-2xl shadow-sm">
                {userInitial}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{user.name}</h2>
                <p className="text-gray-600 text-sm flex items-center gap-1.5 mt-0.5">
                  <Mail size={14} className="text-gray-400" />
                  {user.email}
                </p>
                <p className="text-xs text-emerald-700 font-semibold mt-1">
                  Org: {user.organization || 'Cloud Infrastructure'}
                </p>
              </div>
            </div>

            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="inline-flex items-center px-4 py-2 text-sm font-semibold text-[#2D6A4F] bg-emerald-50 hover:bg-emerald-100 rounded-lg border border-emerald-200 transition-colors w-fit"
              >
                <Edit2 size={16} className="mr-2" />
                Edit Profile
              </button>
            )}
          </div>
        </div>

        {/* Profile Information / Edit Form */}
        <div className="p-6">
          {isEditing ? (
            <form onSubmit={handleSubmit} className="space-y-6">
              {validationError && (
                <div className="p-3 bg-red-50 border-l-4 border-red-500 text-red-700 text-sm rounded">
                  {validationError}
                </div>
              )}

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Full Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#2D6A4F] focus:border-transparent text-sm"
                  placeholder="Enter your full name"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Organization / Company
                </label>
                <input
                  type="text"
                  value={formData.organization}
                  onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#2D6A4F] focus:border-transparent text-sm"
                  placeholder="e.g. Enterprise Cloud Architecture"
                />
                <p className="text-xs text-gray-500 mt-1">This organization name is automatically populated into your executive PDF sustainability audits.</p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">
                  Email Address
                </label>
                <div className="relative">
                  <input
                    type="email"
                    disabled
                    value={user.email}
                    className="w-full px-4 py-2 bg-gray-100 border border-gray-200 rounded-lg text-gray-500 text-sm cursor-not-allowed pr-10"
                  />
                  <Lock size={16} className="absolute right-3 top-2.5 text-gray-400" />
                </div>
                <p className="text-xs text-gray-500 mt-1">Primary email is tied to your JWT login credentials and is read-only.</p>
              </div>

              <div className="flex items-center gap-3 pt-2">
                <button
                  type="submit"
                  disabled={saving}
                  className="inline-flex items-center px-5 py-2.5 bg-[#2D6A4F] text-white rounded-lg hover:bg-[#1B4332] font-semibold text-sm transition-colors disabled:opacity-50"
                >
                  {saving ? (
                    <>
                      <Loader2 size={16} className="mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save size={16} className="mr-2" />
                      Save Changes
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={handleCancel}
                  disabled={saving}
                  className="inline-flex items-center px-4 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-semibold text-sm transition-colors"
                >
                  <X size={16} className="mr-2" />
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-start space-x-3.5 p-3 rounded-lg hover:bg-gray-50 transition">
                <User className="text-emerald-700 mt-1 flex-shrink-0" size={20} />
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Full Name</p>
                  <p className="text-base text-gray-900 font-bold mt-0.5">{user.name}</p>
                </div>
              </div>

              <div className="flex items-start space-x-3.5 p-3 rounded-lg hover:bg-gray-50 transition">
                <Mail className="text-emerald-700 mt-1 flex-shrink-0" size={20} />
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Email Address</p>
                  <p className="text-base text-gray-900 font-bold mt-0.5">{user.email}</p>
                  <span className="inline-flex items-center gap-1 text-[11px] text-emerald-700 font-semibold mt-0.5">
                    <CheckCircle2 size={12} /> Verified
                  </span>
                </div>
              </div>

              <div className="flex items-start space-x-3.5 p-3 rounded-lg hover:bg-gray-50 transition">
                <Building className="text-emerald-700 mt-1 flex-shrink-0" size={20} />
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Organization</p>
                  <p className="text-base text-gray-900 font-bold mt-0.5">{user.organization || 'Cloud Infrastructure'}</p>
                  <p className="text-xs text-gray-500 mt-0.5">Printed on executive reports</p>
                </div>
              </div>

              <div className="flex items-start space-x-3.5 p-3 rounded-lg hover:bg-gray-50 transition">
                <Calendar className="text-emerald-700 mt-1 flex-shrink-0" size={20} />
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Account Active Since</p>
                  <p className="text-base text-gray-900 font-bold mt-0.5">{memberSinceStr}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* User Telemetry & Audit Activity (Only real data, no fake stats) */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-2 flex items-center gap-2">
          <BarChart3 size={18} className="text-[#2D6A4F]" />
          Account Telemetry &amp; Recent Audit Activity
        </h3>
        
        {auditStats ? (
          <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-3.5 bg-gray-50 rounded-lg border border-gray-100">
              <span className="text-xs text-gray-500 block">Monitored Emissions</span>
              <span className="text-lg font-bold text-gray-900">{Number(auditStats.totalEmissionsKg || 0).toFixed(2)} kg</span>
            </div>
            <div className="p-3.5 bg-gray-50 rounded-lg border border-gray-100">
              <span className="text-xs text-gray-500 block">Energy Tracked</span>
              <span className="text-lg font-bold text-gray-900">{Number(auditStats.totalEnergyKwh || 0).toFixed(2)} kWh</span>
            </div>
            <div className="p-3.5 bg-gray-50 rounded-lg border border-gray-100">
              <span className="text-xs text-gray-500 block">Primary Service</span>
              <span className="text-lg font-bold text-gray-900 truncate block">{auditStats.topService || 'N/A'}</span>
            </div>
            <div className="p-3.5 bg-gray-50 rounded-lg border border-gray-100">
              <span className="text-xs text-gray-500 block">Active Region</span>
              <span className="text-lg font-bold text-gray-900 truncate block">{auditStats.topRegion || 'N/A'}</span>
            </div>
          </div>
        ) : (
          <div className="mt-3 p-4 bg-gray-50 rounded-lg border border-gray-200 text-sm text-gray-600">
            <p className="font-semibold text-gray-800">No workload analyses uploaded in this browser yet.</p>
            <p className="text-xs text-gray-500 mt-1">Run the 6-stage demo from the Overview screen or upload an AWS Cost &amp; Usage Report to view real account emission telemetry.</p>
          </div>
        )}
      </div>
    </div>
  );
}
