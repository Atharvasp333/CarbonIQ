import { useState, useEffect, useRef } from 'react';
import { CheckCircle, RefreshCw, Trash2, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import { fetchAWSData } from '../api/client';
import { useAuth } from '../hooks/useAuth';
import axios from 'axios';
import toast from 'react-hot-toast';

const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const REGIONS = [
  'ap-south-1','ap-south-2','ap-southeast-1','ap-southeast-2','ap-southeast-3',
  'ap-northeast-1','ap-northeast-2','ap-northeast-3','ap-east-1',
  'us-east-1','us-east-2','us-west-1','us-west-2',
  'eu-west-1','eu-west-2','eu-west-3','eu-central-1','eu-central-2',
  'eu-north-1','eu-south-1','eu-south-2',
  'ca-central-1','ca-west-1','sa-east-1',
  'me-south-1','me-central-1','af-south-1','il-central-1',
];

// DB-backed helpers — email passed in body, no JWT needed
async function dbGetCreds(email) {
  const r = await axios.post(`${BASE}/api/aws/creds/get`, { email });
  return r.data;
}
async function dbSaveCreds(email, creds) {
  await axios.post(`${BASE}/api/aws/creds/save`, { email, ...creds });
}
async function dbDeleteCreds(email) {
  await axios.post(`${BASE}/api/aws/creds/delete`, { email });
}

export default function AWSConnectBanner({ onDataLoaded }) {
  const { user } = useAuth();
  const [status, setStatus] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [regionSuggestions, setRegionSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const regionRef = useRef(null);
  const [form, setForm] = useState({
    access_key: '', secret_key: '', region: 'ap-south-1', bucket_name: '', file_key: '',
  });

  useEffect(() => {
    if (!user?.email) return;
    dbGetCreds(user.email)
      .then(d => setStatus(d.connected ? d : false))
      .catch(() => setStatus(false));
  }, [user?.email]);

  useEffect(() => {
    const handler = (e) => {
      if (regionRef.current && !regionRef.current.contains(e.target)) setShowSuggestions(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleRegionInput = (val) => {
    setForm({ ...form, region: val });
    const filtered = REGIONS.filter(r => r.includes(val.toLowerCase().trim()));
    setRegionSuggestions(filtered.slice(0, 6));
    setShowSuggestions(filtered.length > 0 && val.length > 0);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.access_key || !form.secret_key || !form.bucket_name) {
      toast.error('Fill in all required fields');
      return;
    }
    setSaving(true);
    try {
      toast.loading('Connecting to S3 & running pipeline…', { id: 'save' });
      // Verify + fetch data
      const data = await fetchAWSData({
        access_key: form.access_key,
        secret_key: form.secret_key,
        region: form.region,
        bucket_name: form.bucket_name,
        file_key: form.file_key || null,
      });
      toast.dismiss('save');

      // Save to NeonDB
      await dbSaveCreds(user.email, {
        access_key: form.access_key,
        secret_key: form.secret_key,
        region: form.region,
        bucket_name: form.bucket_name,
        file_key: form.file_key || null,
      });

      const fresh = await dbGetCreds(user.email);
      setStatus(fresh.connected ? fresh : false);
      setShowForm(false);
      setForm({ access_key: '', secret_key: '', region: 'ap-south-1', bucket_name: '', file_key: '' });
      toast.success('AWS connected!');

      if (data) {
        localStorage.setItem('awsAnalysisData', JSON.stringify(data));
        localStorage.setItem('hasLoadedData', 'true');
        onDataLoaded?.(data);
      }
    } catch (err) {
      toast.dismiss('save');
      toast.error(err.response?.data?.detail || err.message || 'Could not connect to S3');
    } finally {
      setSaving(false);
    }
  };

  const handleSync = async () => {
    if (!status) return;
    setSyncing(true);
    try {
      toast.loading('Fetching & processing CUR from S3…', { id: 'sync' });
      const data = await fetchAWSData({
        access_key: status.access_key,
        secret_key: status.secret_key,
        region: status.region,
        bucket_name: status.bucket_name,
        file_key: null,
      });
      toast.dismiss('sync');
      localStorage.setItem('awsAnalysisData', JSON.stringify(data));
      localStorage.setItem('hasLoadedData', 'true');
      const kg = data?.summary?.total_emissions_kg?.toFixed(2);
      toast.success(kg ? `Synced! ${kg} kg CO₂` : 'S3 data synced!');
      onDataLoaded?.(data);
    } catch (err) {
      toast.dismiss('sync');
      toast.error(err.response?.data?.detail || 'Sync failed');
    } finally {
      setSyncing(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm('Remove saved AWS credentials?')) return;
    await dbDeleteCreds(user.email).catch(() => {});
    setStatus(false);
    toast.success('AWS credentials removed');
  };

  if (!user || status === null) return null;

  // ── CONNECTED ──────────────────────────────────────────────────────────────
  if (status) {
    return (
      <div className="bg-gradient-to-r from-emerald-50 to-green-50 border-2 border-emerald-300 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="bg-emerald-100 p-2 rounded-lg">
            <CheckCircle className="w-5 h-5 text-emerald-600" />
          </div>
          <div>
            <p className="font-semibold text-gray-900 text-sm">AWS Connected</p>
            <p className="text-xs text-gray-500">
              {status.bucket_name} · {status.region} · {status.access_key_masked}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={handleSync} disabled={syncing}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-all">
            <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing…' : 'Sync Now'}
          </button>
          <button onClick={handleDisconnect}
            className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all" title="Disconnect">
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  // ── NOT CONNECTED ──────────────────────────────────────────────────────────
  return (
    <div className="border-2 border-dashed border-amber-300 bg-amber-50 rounded-xl overflow-hidden">
      <button onClick={() => setShowForm(v => !v)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-amber-100 transition-colors">
        <div className="flex items-center gap-3">
          <div className="bg-amber-100 p-2 rounded-lg">
            <AlertCircle className="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <p className="font-semibold text-gray-900 text-sm">Connect AWS for automatic CUR sync</p>
            <p className="text-xs text-gray-500">Link your S3 bucket — syncs across all devices</p>
          </div>
        </div>
        <span className="flex items-center gap-1 text-sm text-amber-700 font-medium">
          {showForm
            ? <><ChevronUp className="w-4 h-4" /><span>Hide</span></>
            : <><ChevronDown className="w-4 h-4" /><span>Connect</span></>}
        </span>
      </button>

      {showForm && (
        <form onSubmit={handleSave} className="border-t border-amber-200 p-4 bg-white space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">AWS Access Key ID</label>
              <input type="text" value={form.access_key}
                onChange={e => setForm({ ...form, access_key: e.target.value })}
                placeholder="AKIAIOSFODNN7EXAMPLE"
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                required />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">AWS Secret Access Key</label>
              <input type="password" value={form.secret_key}
                onChange={e => setForm({ ...form, secret_key: e.target.value })}
                placeholder="wJalrXUtnFEMI/K7MDENG/…"
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                required />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">AWS Region</label>
              <div className="relative" ref={regionRef}>
                <input type="text" value={form.region}
                  onChange={e => handleRegionInput(e.target.value)}
                  onFocus={() => {
                    const f = REGIONS.filter(r => r.includes(form.region.toLowerCase()));
                    setRegionSuggestions(f.slice(0, 6));
                    setShowSuggestions(f.length > 0);
                  }}
                  placeholder="e.g. ap-south-1"
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                  required />
                {showSuggestions && (
                  <ul className="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-40 overflow-y-auto">
                    {regionSuggestions.map(r => (
                      <li key={r} onMouseDown={() => { setForm({ ...form, region: r }); setShowSuggestions(false); }}
                        className="px-3 py-2 text-sm text-gray-700 hover:bg-emerald-50 hover:text-emerald-700 cursor-pointer">
                        {r}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">S3 Bucket Name</label>
              <input type="text" value={form.bucket_name}
                onChange={e => setForm({ ...form, bucket_name: e.target.value })}
                placeholder="my-cur-bucket"
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                required />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              S3 File Path <span className="text-gray-400 font-normal">(optional — auto-detects latest)</span>
            </label>
            <input type="text" value={form.file_key}
              onChange={e => setForm({ ...form, file_key: e.target.value })}
              placeholder="reports/CUR_report/20260601-20260701/CUR_report-00001.csv.gz"
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent font-mono" />
          </div>
          <div className="flex items-center justify-between flex-wrap gap-3">
            <p className="text-xs text-gray-500">
              Needs <code className="bg-gray-100 px-1 rounded">s3:GetObject</code> + <code className="bg-gray-100 px-1 rounded">s3:ListBucket</code>.
              Credentials saved to your account — works on all devices.
            </p>
            <div className="flex gap-2 flex-shrink-0">
              <button type="button" onClick={() => setShowForm(false)}
                className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg">
                Cancel
              </button>
              <button type="submit" disabled={saving}
                className="px-4 py-2 text-sm font-medium bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-lg transition-all">
                {saving ? 'Connecting…' : 'Connect & Sync'}
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
}
