import React, { useState } from 'react';
import { Upload, Activity, TrendingDown, AlertCircle, Zap, MapPin } from 'lucide-react';
import axios from 'axios';
import ServiceDetailDashboard from './ServiceDetailDashboard';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 120000
});

const MultiAgentDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState('');
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [serviceDetailName, setServiceDetailName] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    setLoading(true);
    setError(null);
    setResults(null);
    setProgress('Uploading and processing CSV...');
    try {
      const formData = new FormData();
      formData.append('file', file);
      setProgress('Processing through multi-agent pipeline...');
      const response = await apiClient.post('/api/multi-agent/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      if (response.data?.success === false) throw new Error(response.data.message || 'Analysis failed');
      if (response.data?.summary) {
        setResults(response.data);
        try { await apiClient.post('/api/service-analytics/store', response.data); } catch (_) {}
      } else {
        throw new Error('Invalid response format from server');
      }
      setProgress('');
    } catch (err) {
      setError(err.response?.data?.message || err.response?.data?.detail || err.message || 'Analysis failed');
      setProgress('');
    } finally {
      setLoading(false);
    }
  };

  const loadDemoData = async () => {
    setLoading(true);
    setError(null);
    setResults(null);
    setProgress('Loading demo CUR data...');
    try {
      setProgress('Processing demo data through pipeline...');
      const response = await apiClient.post('/api/multi-agent/analyze-demo', { load_demo: true });
      if (response.data?.success === false) throw new Error(response.data.message || 'Demo load failed');
      if (response.data?.summary) {
        setResults(response.data);
        try { await apiClient.post('/api/service-analytics/store', response.data); } catch (_) {}
      } else {
        throw new Error('Invalid response format from server');
      }
      setProgress('');
    } catch (err) {
      setError(err.response?.data?.message || err.response?.data?.detail || err.message || 'Demo load failed');
      setProgress('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 p-8">
      <div className="max-w-7xl mx-auto">

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-4">Multi-Agent Carbon Intelligence</h1>
          <p className="text-xl text-blue-300">AI-Powered AWS CUR Analysis with 6 Specialized Agents</p>
        </div>

        {/* Upload Section */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 mb-8 border border-white/20">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-center">
            <label className="flex-1 max-w-md">
              <div className="flex items-center justify-center gap-3 px-6 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl cursor-pointer transition-all duration-200 transform hover:scale-105">
                <Upload size={24} />
                <span className="font-semibold">Upload AWS CUR CSV</span>
              </div>
              <input type="file" accept=".csv" onChange={handleFileUpload} className="hidden" disabled={loading} />
            </label>
            <button
              onClick={loadDemoData}
              disabled={loading}
              className="flex items-center gap-3 px-6 py-4 bg-green-600 hover:bg-green-700 text-white rounded-xl transition-all duration-200 transform hover:scale-105 disabled:opacity-50"
            >
              <Activity size={24} />
              <span className="font-semibold">Load Demo CUR</span>
            </button>
          </div>

          {loading && (
            <div className="mt-6 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
              <p className="text-white mt-4 text-lg font-semibold">{progress || 'Processing...'}</p>
            </div>
          )}

          {error && (
            <div className="mt-6 p-4 bg-red-500/20 border border-red-500 rounded-lg">
              <p className="text-red-200 font-semibold mb-2">Error</p>
              <p className="text-red-100">{error}</p>
            </div>
          )}
        </div>

        {/* Results */}
        {results && results.success && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <SummaryCard
                title="Total Emissions"
                value={`${results.summary.total_emissions_kg.toFixed(4)} kg`}
                subtitle={`CO₂ · ${results.pipeline_stats.ingestion.original_rows} rows scanned`}
                icon={<Activity className="text-red-400" size={32} />}
                bgColor="bg-red-500/20"
              />
              <SummaryCard
                title="Total Cost"
                value={`$${results.summary.total_cost.toFixed(4)}`}
                subtitle="AWS Spend"
                icon={<TrendingDown className="text-green-400" size={32} />}
                bgColor="bg-green-500/20"
              />
              <SummaryCard
                title="Top Region"
                value={results.summary.top_region}
                subtitle="Highest Emitter"
                icon={<MapPin className="text-blue-400" size={32} />}
                bgColor="bg-blue-500/20"
              />
              <SummaryCard
                title="Top Service"
                value={results.summary.top_service}
                subtitle="Highest Usage"
                icon={<Zap className="text-yellow-400" size={32} />}
                bgColor="bg-yellow-500/20"
              />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Emissions by Service */}
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                <h3 className="text-2xl font-bold text-white mb-4">Emissions by Service</h3>
                <div className="space-y-3">
                  {results.analytics.service_breakdown.slice(0, 8).map((service, idx) => (
                    <div
                      key={idx}
                      className="bg-white/5 rounded-lg p-4 cursor-pointer hover:bg-white/10 transition-all"
                      onClick={() => setServiceDetailName(service.service)}
                    >
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-white font-semibold flex items-center gap-2">
                          {service.service}
                          <span className="text-xs text-blue-400">click for details →</span>
                        </span>
                        <span className="text-green-300">{service.emissions_kg.toFixed(4)} kg</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-red-500 to-orange-500 h-2 rounded-full"
                          style={{ width: `${results.summary.total_emissions_kg > 0 ? (service.emissions_kg / results.summary.total_emissions_kg) * 100 : 0}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-xs text-gray-400 mt-1">
                        <span>Cost: ${service.cost.toFixed(4)}</span>
                        <span>Energy: {service.energy_kwh.toFixed(4)} kWh</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Emissions by Region */}
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                <h3 className="text-2xl font-bold text-white mb-4">Emissions by Region</h3>
                <div className="space-y-3">
                  {results.analytics.region_breakdown.slice(0, 8).map((region, idx) => (
                    <div key={idx} className="bg-white/5 rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-white font-semibold">{region.region}</span>
                        <span className="text-blue-300">{region.emissions_kg.toFixed(4)} kg</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                          style={{ width: `${results.summary.total_emissions_kg > 0 ? (region.emissions_kg / results.summary.total_emissions_kg) * 100 : 0}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-xs text-gray-400 mt-1">
                        <span>Zone: {region.zone}</span>
                        <span>Intensity: {region.avg_carbon_intensity} gCO₂/kWh</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Optimization */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 mb-8">
              <h3 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <TrendingDown className="text-green-400" />
                Optimization Opportunities
              </h3>
              <div className="bg-green-500/20 border border-green-500 rounded-lg p-4 mb-6">
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-3xl font-bold text-white">{results.optimization.reduction_estimates.total_potential_reduction_kg.toFixed(4)} kg</div>
                    <div className="text-green-300">CO₂ Reduction</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-white">${results.optimization.reduction_estimates.total_potential_cost_savings.toFixed(4)}</div>
                    <div className="text-green-300">Cost Savings</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-white">{results.optimization.reduction_estimates.percentage_reduction.toFixed(1)}%</div>
                    <div className="text-green-300">Reduction Rate</div>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                {results.optimization.opportunities.slice(0, 5).map((opp, idx) => (
                  <div key={idx} className="bg-white/5 rounded-lg p-4 border-l-4 border-yellow-500">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="text-yellow-400 mt-1" size={20} />
                      <div className="flex-1">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-semibold text-white capitalize">{opp.type?.replace('_', ' ')}</span>
                          <span className={`px-2 py-1 rounded text-xs font-bold ${opp.priority === 'high' ? 'bg-red-500' : 'bg-yellow-500'} text-white`}>
                            {opp.priority?.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-gray-300 text-sm">{opp.description}</p>
                        {opp.reduction_kg && (
                          <div className="mt-2 text-green-400 text-sm font-semibold">
                            Save {opp.reduction_kg.toFixed(4)} kg CO₂
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Detailed Table */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 mb-8">
              <h3 className="text-2xl font-bold text-white mb-4">Detailed Workload Analysis</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-white/20">
                      <th className="pb-3 text-gray-300">Service</th>
                      <th className="pb-3 text-gray-300">Region</th>
                      <th className="pb-3 text-gray-300">Date</th>
                      <th className="pb-3 text-gray-300">Usage</th>
                      <th className="pb-3 text-gray-300">Cost</th>
                      <th className="pb-3 text-gray-300">C.Intensity</th>
                      <th className="pb-3 text-gray-300">Emissions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.detailed_records.slice(0, 30).map((record, idx) => (
                      <tr key={idx} className="border-b border-white/10 hover:bg-white/5">
                        <td className="py-2 text-white">{record.service}</td>
                        <td className="py-2 text-gray-300">{record.region}</td>
                        <td className="py-2 text-gray-400">{record.timestamp?.split('T')[0] || '—'}</td>
                        <td className="py-2 text-gray-300">{(record.usage_amount ?? 0).toFixed(4)}</td>
                        <td className="py-2 text-green-300">${(record.cost ?? 0).toFixed(4)}</td>
                        <td className="py-2 text-yellow-300">{record.carbon_intensity} g/kWh</td>
                        <td className="py-2 text-red-300">{(record.emissions_kg ?? 0).toFixed(6)} kg</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Pipeline Stats */}
            <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10 mb-8">
              <h4 className="text-lg font-bold text-gray-400 mb-4">Pipeline Performance</h4>
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-center mb-4">
                <StatBadge label="Rows Scanned" value={results.pipeline_stats.ingestion.original_rows} />
                <StatBadge label="Valid Rows" value={results.pipeline_stats.ingestion.processed_rows} />
                <StatBadge label="Compressed To" value={results.pipeline_stats.ingestion.compressed_rows} />
                <StatBadge label="API Calls" value={results.pipeline_stats.carbon_intensity.api_calls} />
                <StatBadge label="Cache Hits" value={results.pipeline_stats.carbon_intensity.cached_calls} />
                <StatBadge label="Fallbacks" value={results.pipeline_stats.carbon_intensity.failed_calls} />
              </div>

              {/* API Call Log */}
              {results.pipeline_stats.carbon_intensity.api_call_log?.length > 0 && (
                <div>
                  <h5 className="text-gray-400 text-sm font-semibold mb-2">Electricity Maps API Call Log</h5>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                      <thead>
                        <tr className="border-b border-white/10 text-gray-500">
                          <th className="pb-2 pr-4">Zone</th>
                          <th className="pb-2 pr-4">Date</th>
                          <th className="pb-2 pr-4">Called At (UTC)</th>
                          <th className="pb-2 pr-4">Status</th>
                          <th className="pb-2 pr-4">Carbon Intensity</th>
                          <th className="pb-2 pr-4">Response Time</th>
                          <th className="pb-2">Source</th>
                        </tr>
                      </thead>
                      <tbody>
                        {results.pipeline_stats.carbon_intensity.api_call_log.map((entry, idx) => (
                          <tr key={idx} className="border-b border-white/5">
                            <td className="py-1 pr-4 text-white font-mono">{entry.zone}</td>
                            <td className="py-1 pr-4 text-gray-300">{entry.date || '—'}</td>
                            <td className="py-1 pr-4 text-gray-300">{entry.called_at?.replace('T', ' ').split('.')[0]}</td>
                            <td className="py-1 pr-4">
                              <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                                entry.status === 'success' ? 'bg-green-500/30 text-green-300' :
                                entry.status === 'failed' ? 'bg-red-500/30 text-red-300' :
                                'bg-gray-500/30 text-gray-400'}`}>
                                {entry.status}
                              </span>
                            </td>
                            <td className="py-1 pr-4 text-yellow-300">{entry.carbon_intensity} gCO₂/kWh</td>
                            <td className="py-1 pr-4 text-gray-300">{entry.response_ms != null ? `${entry.response_ms}ms` : '—'}</td>
                            <td className="py-1 text-blue-300">{entry.source}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </>
        )}

        {/* Service Detail Modal */}
        {serviceDetailName && (
          <div
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 overflow-y-auto p-4"
            onClick={() => setServiceDetailName(null)}
          >
            <div
              className="bg-gradient-to-br from-gray-900 to-blue-900 rounded-2xl border border-white/20 max-w-6xl mx-auto my-8 p-6"
              onClick={e => e.stopPropagation()}
            >
              <ServiceDetailDashboard
                serviceName={serviceDetailName}
                onClose={() => setServiceDetailName(null)}
              />
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

const SummaryCard = ({ title, value, subtitle, icon, bgColor }) => (
  <div className={`${bgColor} backdrop-blur-lg rounded-2xl p-6 border border-white/20`}>
    <div className="flex items-start justify-between mb-4">
      <div className="flex-1">
        <p className="text-gray-300 text-sm mb-1">{title}</p>
        <h3 className="text-2xl font-bold text-white">{value}</h3>
        <p className="text-gray-400 text-xs mt-1">{subtitle}</p>
      </div>
      <div>{icon}</div>
    </div>
  </div>
);

const StatBadge = ({ label, value }) => (
  <div className="bg-white/5 rounded-lg p-3">
    <div className="text-2xl font-bold text-white">{value}</div>
    <div className="text-xs text-gray-400">{label}</div>
  </div>
);

export default MultiAgentDashboard;
