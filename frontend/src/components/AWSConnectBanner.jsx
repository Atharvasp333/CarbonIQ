import { useState, useEffect } from 'react';
import { Cloud, CheckCircle, X, RefreshCw, Trash2, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import { getAWSCredentials, saveAWSCredentials, deleteAWSCredentials, autoSyncAWS } from '../api/client';
import toast from 'react-hot-toast';

const REGIONS = [
  { value: 'us-east-1', label: 'US East (N. Virginia)' },
  { value: 'us-east-2', label: 'US East (Ohio)' },
  { value: 'us-west-1', label: 'US West (N. California)' },
  { value: 'us-west-2', label: 'US West (Oregon)' },
  { value: 'eu-west-1', label: 'EU (Ireland)' },
  { value: 'eu-central-1', label: 'EU (Frankfurt)' },
  { value: 'ap-south-1', label: 'Asia Pacific (Mumbai)' },
  { value: 'ap-southeast-1', label: 'Asia Pacific (Singapore)' },
  { value: 'ap-northeast-1', label: 'Asia Pacific (Tokyo)' },
];

export default function AWSConnectBanner({ onDataLoaded }) {
  const [status, setStatus] = useState(null); // null = loading, false = not connected, object = connected
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [form, setForm] = useState({
    access_key: '',
    secret_key: '',
    region: 'us-east-1',
    bucket_name: '',
  });

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const data = await getAWSCredentials();
      setStatus(data.connected ? data : false);
    } catch {
      setStatus(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.access_key || !form.secret_key || !form.bucket_name) {
      toast.error('Fill in all fields');
      return;
    }
    setSaving(true);
    try {
      await saveAWSCredentials(form);
      toast.success('AWS connected and verified!');
      setShowForm(false);
      setForm({ access_key: '', secret_key: '', region: 'us-east-1', bucket_name: '' });
      await loadStatus();
      // Auto-trigger sync after connecting
      await handleSync();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not connect to AWS');
    } finally {
      setSaving(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      toast.loading('Fetching latest CUR from S3...', { id: 'sync' });
      const data = await autoSyncAWS();
      toast.dismiss('sync');
      if (data?.success !== false) {
        localStorage.setItem('awsAnalysisData', JSON.stringify(data));
        localStorage.setItem('hasLoadedData', 'true');
        toast.success('S3 data synced and analyzed!');
        onDataLoaded?.(data);
      } else {
        toast.error(data.message || 'Sync failed');
      }
    } catch (err) {
      toast.dismiss('sync');
      toast.error(err.response?.data?.detail || 'Auto-sync failed');
    } finally {
      setSyncing(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm('Remove your saved AWS credentials?')) return;
    try {
      await deleteAWSCredentials();
      setStatus(false);
      toast.success('AWS credentials removed');
    } catch {
      toast.error('Failed to remove credentials');
    }
  };

  // Still loading
  if (status === null) return null;

  // ── CONNECTED STATE ────────────────────────────────────────────────────────
  if (status && status.connected) {
    return (
      <div className="bg-gradient-to-r from-emerald-50 to-green-50 border-2 border-emerald-300 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="bg-emerald-100 p-2 rounded-lg">
            <CheckCircle className="w-5 h-5 text-emerald-600" />
          </div>
          <div>
            <p className="font-semibold text-gray-900 text-sm">AWS Connected</p>
            <p className="text-xs text-gray-500">
              {status.bucket_name} · {status.region} · key {status.access_key_masked}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleSync}
            disabled={syncing}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync Now'}
          </button>
          <button
            onClick={handleDisconnect}
            className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all"
            title="Disconnect AWS"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  // ── NOT CONNECTED STATE ────────────────────────────────────────────────────
  return (
    <div className="border-2 border-dashed border-amber-300 bg-amber-50 rounded-xl overflow-hidden">
      {/* Header row */}
      <button
        onClick={() => setShowForm((v) => !v)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-amber-100 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="bg-amber-100 p-2 rounded-lg">
            <AlertCircle className="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <p className="font-semibold text-gray-900 text-sm">Connect AWS for automatic CUR sync</p>
            <p className="text-xs text-gray-500">
              Link your S3 bucket once — we'll auto-fetch your latest CUR on every session
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm text-amber-700 font-medium">
          {showForm ? (
            <><ChevronUp className="w-4 h-4" /> Hide</>
          ) : (
            <><ChevronDown className="w-4 h-4" /> Connect</>
          )}
        </div>
      </button>

      {/* Credential form */}
      {showForm && (
        <form onSubmit={handleSave} className="border-t border-amber-200 p-4 bg-white space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">AWS Access Key ID</label>
              <input
                type="text"
                value={form.access_key}
                onChange={(e) => setForm({ ...form, access_key: e.target.value })}
                placeholder="AKIAIOSFODNN7EXAMPLE"
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">AWS Secret Access Key</label>
              <input
                type="password"
                value={form.secret_key}
                onChange={(e) => setForm({ ...form, secret_key: e.target.value })}
                placeholder="wJalrXUtnFEMI/K7MDENG/..."
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">AWS Region</label>
              <select
                value={form.region}
                onChange={(e) => setForm({ ...form, region: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              >
                {REGIONS.map((r) => (
                  <option key={r.value} value={r.value}>{r.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">S3 Bucket Name</label>
              <input
                type="text"
                value={form.bucket_name}
                onChange={(e) => setForm({ ...form, bucket_name: e.target.value })}
                placeholder="my-cur-bucket"
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          <div className="flex items-center justify-between">
            <p className="text-xs text-gray-500">
              Needs <code className="bg-gray-100 px-1 rounded">s3:GetObject</code> + <code className="bg-gray-100 px-1 rounded">s3:ListBucket</code> on your CUR bucket.
              Keys are verified then stored in your account — never logged.
            </p>
            <div className="flex gap-2 ml-4 flex-shrink-0">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="px-4 py-2 text-sm font-medium bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-lg transition-all"
              >
                {saving ? 'Verifying...' : 'Connect & Sync'}
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
}
