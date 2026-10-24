import React, { useState, useEffect } from 'react';
import { 
  Terminal, 
  Key, 
  Copy, 
  Check, 
  Trash2, 
  RefreshCw, 
  Zap, 
  Leaf, 
  Clock, 
  Activity, 
  ExternalLink,
  Code2,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';
import toast from 'react-hot-toast';
import { 
  listApiKeys, 
  createApiKey, 
  revokeApiKey, 
  getCliStats, 
  getCliHistory 
} from '../../api/client';

export default function CLIWorkloads() {
  const [keys, setKeys] = useState([]);
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generatingKey, setGeneratingKey] = useState(false);
  const [newKeyData, setNewKeyData] = useState(null);
  const [copiedKey, setCopiedKey] = useState(false);
  const [copiedSnippet, setCopiedSnippet] = useState(null);
  const [activeTab, setActiveTab] = useState('cli');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [keysRes, statsRes, histRes] = await Promise.all([
        listApiKeys().catch(() => ({ keys: [] })),
        getCliStats().catch(() => null),
        getCliHistory(30).catch(() => ({ measurements: [] }))
      ]);
      setKeys(keysRes?.keys || []);
      setStats(statsRes || null);
      setHistory(histRes?.measurements || []);
    } catch (err) {
      console.error('Error fetching CLI workload data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateKey = async () => {
    setGeneratingKey(true);
    try {
      const res = await createApiKey(`CLI Key ${keys.length + 1}`);
      if (res?.success) {
        setNewKeyData(res);
        toast.success('API Key generated successfully!');
        fetchData();
      }
    } catch (err) {
      toast.error('Failed to generate API Key');
    } finally {
      setGeneratingKey(false);
    }
  };

  const handleRevokeKey = async (keyId) => {
    if (!window.confirm('Are you sure you want to revoke this API key? Any CLI connected with it will stop syncing.')) {
      return;
    }
    try {
      await revokeApiKey(keyId);
      toast.success('API Key revoked');
      fetchData();
    } catch (err) {
      toast.error('Failed to revoke API Key');
    }
  };

  const handleCopy = (text, id = 'key') => {
    navigator.clipboard.writeText(text);
    if (id === 'key') {
      setCopiedKey(true);
      setTimeout(() => setCopiedKey(false), 2000);
    } else {
      setCopiedSnippet(id);
      setTimeout(() => setCopiedSnippet(null), 2000);
    }
    toast.success('Copied to clipboard');
  };

  const defaultKeyForSnippet = newKeyData?.api_key || (keys[0] ? `${keys[0].key_prefix}...` : 'ciq_live_your_api_key_here');

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 bg-[#1B4332]/10 text-[#1B4332] rounded-lg">
              <Terminal size={24} />
            </span>
            <h1 className="text-3xl font-bold text-gray-900">CLI & Workloads</h1>
          </div>
          <p className="text-gray-600 mt-1">
            Real-time carbon emissions & energy tracking from your local terminal, CI/CD, and scripts.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 bg-white hover:bg-gray-50 transition-colors shadow-sm disabled:opacity-50"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
          <button
            onClick={handleCreateKey}
            disabled={generatingKey}
            className="flex items-center gap-2 px-4 py-2 bg-[#1B4332] hover:bg-[#2D6A4F] text-white font-medium rounded-lg transition-colors shadow-sm disabled:opacity-50"
          >
            <Key size={16} />
            {generatingKey ? 'Generating...' : 'Generate API Key'}
          </button>
        </div>
      </div>

      {/* New Key Alert Banner */}
      {newKeyData && (
        <div className="bg-emerald-50 border border-emerald-300 rounded-xl p-5 shadow-sm">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-emerald-900 font-semibold">
                <ShieldCheck size={20} className="text-emerald-700" />
                New API Key Generated
              </div>
              <p className="text-sm text-emerald-800">
                Please copy and store your API key now. For security, you will not be able to view it again.
              </p>
              <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg border border-emerald-200 font-mono text-sm text-gray-800 max-w-xl">
                <span className="truncate">{newKeyData.api_key}</span>
                <button
                  onClick={() => handleCopy(newKeyData.api_key, 'key')}
                  className="ml-auto text-emerald-700 hover:text-emerald-900 p-1"
                  title="Copy Key"
                >
                  {copiedKey ? <Check size={18} className="text-emerald-600" /> : <Copy size={18} />}
                </button>
              </div>
            </div>
            <button
              onClick={() => setNewKeyData(null)}
              className="text-emerald-700 hover:text-emerald-900 text-sm font-medium"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
            <Activity size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Total Workloads</p>
            <p className="text-2xl font-bold text-gray-900">
              {stats?.total_measurements ?? (loading ? '...' : 0)}
            </p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
            <Leaf size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Total Emissions</p>
            <p className="text-2xl font-bold text-gray-900">
              {stats?.total_emissions_gco2e != null 
                ? `${Number(stats.total_emissions_gco2e).toFixed(2)} g`
                : (loading ? '...' : '0.00 g')}
            </p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
            <Zap size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Energy Consumed</p>
            <p className="text-2xl font-bold text-gray-900">
              {stats?.total_energy_kwh != null 
                ? `${Number(stats.total_energy_kwh).toFixed(6)} kWh`
                : (loading ? '...' : '0.00 kWh')}
            </p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0">
            <Clock size={24} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Avg Duration</p>
            <p className="text-2xl font-bold text-gray-900">
              {stats?.avg_duration_seconds != null 
                ? `${Number(stats.avg_duration_seconds).toFixed(2)}s`
                : (loading ? '...' : '0.00s')}
            </p>
          </div>
        </div>
      </div>

      {/* Integration Guide & API Keys Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quickstart Guide (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col">
          <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Code2 size={20} className="text-[#1B4332]" />
              <h2 className="text-lg font-semibold text-gray-900">Quick Setup & Usage</h2>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('cli')}
                className={`px-3 py-1 text-xs font-semibold rounded-md transition-colors ${
                  activeTab === 'cli' ? 'bg-[#1B4332] text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                CLI Tool
              </button>
              <button
                onClick={() => setActiveTab('sdk')}
                className={`px-3 py-1 text-xs font-semibold rounded-md transition-colors ${
                  activeTab === 'sdk' ? 'bg-[#1B4332] text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Python SDK
              </button>
            </div>
          </div>

          <div className="p-6 bg-gray-900 text-gray-100 font-mono text-xs overflow-x-auto space-y-4 flex-1">
            {activeTab === 'cli' ? (
              <>
                <div className="text-gray-400"># 1. Configure your API Key</div>
                <div className="flex items-center justify-between bg-gray-800/80 px-3 py-2 rounded">
                  <code>python cli/carboniq_cli.py config set-key {defaultKeyForSnippet}</code>
                  <button
                    onClick={() => handleCopy(`python cli/carboniq_cli.py config set-key ${defaultKeyForSnippet}`, 'snip1')}
                    className="text-gray-400 hover:text-white ml-2"
                  >
                    {copiedSnippet === 'snip1' ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                  </button>
                </div>

                <div className="text-gray-400 pt-2"># 2. Benchmark any script or workload with CodeCarbon</div>
                <div className="flex items-center justify-between bg-gray-800/80 px-3 py-2 rounded">
                  <code>python cli/carboniq_cli.py measure-script sample_workloads/simple_task.py --workload-name "Model Test"</code>
                  <button
                    onClick={() => handleCopy(`python cli/carboniq_cli.py measure-script sample_workloads/simple_task.py --workload-name "Model Test"`, 'snip2')}
                    className="text-gray-400 hover:text-white ml-2"
                  >
                    {copiedSnippet === 'snip2' ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                  </button>
                </div>

                <div className="text-gray-400 pt-2"># 3. Live terminal grid carbon intensity monitor</div>
                <div className="flex items-center justify-between bg-gray-800/80 px-3 py-2 rounded">
                  <code>python cli/carboniq_cli.py monitor --region us-east-1 --interval 5</code>
                  <button
                    onClick={() => handleCopy(`python cli/carboniq_cli.py monitor --region us-east-1 --interval 5`, 'snip3')}
                    className="text-gray-400 hover:text-white ml-2"
                  >
                    {copiedSnippet === 'snip3' ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="text-gray-400"># Use CarbonIQ Decorator in your code</div>
                <div className="bg-gray-800/80 p-3 rounded space-y-1">
                  <div className="text-purple-300">import <span className="text-white">carboniq</span></div>
                  <br />
                  <div className="text-emerald-400">@carboniq.track<span className="text-white">(workload_name=</span><span className="text-amber-300">"data_processing"</span><span className="text-white">)</span></div>
                  <div><span className="text-blue-400">def</span> <span className="text-yellow-300">run_heavy_compute</span>():</div>
                  <div className="pl-4 text-gray-300"># Computation runs with live emissions tracking</div>
                  <div className="pl-4 text-gray-300">return process_data()</div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* API Keys Table (1 col) */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Key size={18} className="text-[#1B4332]" />
                <h3 className="font-semibold text-gray-900">Your API Keys</h3>
              </div>
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full font-medium">
                {keys.length} active
              </span>
            </div>

            {keys.length === 0 ? (
              <div className="text-center py-8 text-gray-500 text-sm">
                <Key size={32} className="mx-auto text-gray-300 mb-2" />
                No API keys generated yet. Click "Generate API Key" to connect your CLI.
              </div>
            ) : (
              <div className="space-y-3">
                {keys.map((k) => (
                  <div
                    key={k.id}
                    className="p-3 border border-gray-200 rounded-lg bg-gray-50 flex items-center justify-between text-sm"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{k.name}</p>
                      <p className="font-mono text-xs text-gray-500">{k.key_prefix}</p>
                      <p className="text-[11px] text-gray-400 mt-1">
                        {k.last_used_at ? `Last used: ${new Date(k.last_used_at).toLocaleDateString()}` : 'Never used'}
                      </p>
                    </div>
                    <button
                      onClick={() => handleRevokeKey(k.id)}
                      className="text-red-500 hover:text-red-700 p-1.5 hover:bg-red-50 rounded transition-colors"
                      title="Revoke Key"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-gray-100 text-xs text-gray-500">
            Keys grant authentication from your command line to record workloads under your user profile.
          </div>
        </div>
      </div>

      {/* Realtime Measurement History Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity size={18} className="text-[#1B4332]" />
            <h2 className="text-lg font-semibold text-gray-900">Real-time Measurement Logs</h2>
          </div>
          <span className="text-xs text-gray-500">
            Showing last {history.length} runs
          </span>
        </div>

        {history.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Terminal size={40} className="mx-auto text-gray-300 mb-3" />
            <p className="font-medium text-gray-700">No workload measurements recorded yet</p>
            <p className="text-sm text-gray-500 mt-1 max-w-md mx-auto">
              Run your first measurement from the terminal using <code className="bg-gray-100 px-1 py-0.5 rounded text-gray-700">python cli/carboniq_cli.py measure-script</code> to see live metrics appear here.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600">
              <thead className="bg-gray-50 text-xs uppercase font-semibold text-gray-500 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3">Workload Name</th>
                  <th className="px-6 py-3">Type</th>
                  <th className="px-6 py-3">Duration</th>
                  <th className="px-6 py-3">Emissions</th>
                  <th className="px-6 py-3">Energy</th>
                  <th className="px-6 py-3">Carbon Intensity</th>
                  <th className="px-6 py-3">Recorded At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {history.map((row) => (
                  <tr key={row.id} className="hover:bg-gray-50/80 transition-colors">
                    <td className="px-6 py-4 font-medium text-gray-900 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                      {row.workload_name}
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-700">
                        {row.workload_type || 'general'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {row.duration_seconds != null ? `${Number(row.duration_seconds).toFixed(2)}s` : 'N/A'}
                    </td>
                    <td className="px-6 py-4 font-medium text-emerald-700">
                      {row.emissions_gco2e != null ? `${Number(row.emissions_gco2e).toFixed(4)} g` : '0 g'}
                    </td>
                    <td className="px-6 py-4">
                      {row.energy_kwh != null ? `${Number(row.energy_kwh).toFixed(6)} kWh` : '0 kWh'}
                    </td>
                    <td className="px-6 py-4">
                      {row.carbon_intensity != null ? `${Number(row.carbon_intensity).toFixed(1)} g/kWh` : 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-xs text-gray-500">
                      {row.measured_at ? new Date(row.measured_at).toLocaleString() : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
