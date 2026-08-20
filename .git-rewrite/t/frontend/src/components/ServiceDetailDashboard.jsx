import React, { useState, useEffect } from 'react';
import { ArrowLeft, Activity, DollarSign, Zap, MapPin, AlertTriangle, Clock } from 'lucide-react';
import axios from 'axios';

const apiClient = axios.create({ baseURL: 'http://localhost:8000' });

const ServiceDetailDashboard = ({ serviceName, onClose }) => {
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!serviceName) return;
    setLoading(true);
    setError(null);
    apiClient.get(`/api/service-analytics/${encodeURIComponent(serviceName)}`)
      .then(res => setAnalytics(res.data))
      .catch(err => setError(err.response?.data?.detail || 'Failed to load analytics'))
      .finally(() => setLoading(false));
  }, [serviceName]);

  if (loading) return (
    <div className="flex items-center justify-center py-20">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent mb-4" />
        <p className="text-white text-lg">Loading {serviceName} analytics...</p>
      </div>
    </div>
  );

  if (error) return (
    <div className="bg-red-500/20 border border-red-500 rounded-xl p-6 text-center">
      <AlertTriangle className="mx-auto mb-3 text-red-400" size={40} />
      <p className="text-red-200 font-semibold mb-2">Error</p>
      <p className="text-red-100 text-sm">{error}</p>
    </div>
  );

  if (!analytics) return null;

  const s = analytics.summary || {};
  const timeline = analytics.run_history || [];
  const regionBreakdown = analytics.region_breakdown || [];
  const peakEvents = analytics.peak_emission_events || [];
  const optimization = analytics.optimization_insights || {};
  const whatif = analytics.whatif_scenarios || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white">{analytics.service_name} — Detailed Analysis</h2>
          <p className="text-gray-400 text-sm mt-1">
            {analytics.total_records} daily records
            {s.time_range?.start && ` · ${s.time_range.start?.split('T')[0]} → ${s.time_range.end?.split('T')[0]}`}
          </p>
        </div>
        <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/10">✕</button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SCard label="Total Emissions" value={`${(s.total_emissions_kg ?? 0).toFixed(4)} kg`} color="red" icon={<Activity size={20} />} />
        <SCard label="Total Cost" value={`$${(s.total_cost ?? 0).toFixed(4)}`} color="green" icon={<DollarSign size={20} />} />
        <SCard label="Total Usage" value={(s.total_usage ?? 0).toFixed(2)} color="blue" icon={<Zap size={20} />} />
        <SCard label="Avg Carbon Intensity" value={`${(s.average_carbon_intensity ?? 0).toFixed(0)} gCO₂/kWh`} color="yellow" icon={<MapPin size={20} />} />
      </div>

      {/* Region Breakdown + Peak Events */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Region Breakdown */}
        <div className="bg-white/5 rounded-xl p-5 border border-white/10">
          <h3 className="text-lg font-bold text-white mb-3">Region Breakdown</h3>
          {regionBreakdown.length === 0
            ? <p className="text-gray-400 text-sm">No region data</p>
            : <div className="space-y-2">
                {regionBreakdown.map((r, i) => (
                  <div key={i} className="bg-white/5 rounded-lg p-3">
                    <div className="flex justify-between mb-1">
                      <span className="text-white font-medium">{r.region}</span>
                      <span className="text-red-300 text-sm">{(r.emissions_kg ?? 0).toFixed(4)} kg</span>
                    </div>
                    <div className="flex justify-between text-xs text-gray-400">
                      <span>{r.runs} records · ${(r.cost ?? 0).toFixed(4)}</span>
                      <span>{(r.avg_carbon_intensity ?? 0).toFixed(0)} gCO₂/kWh</span>
                    </div>
                  </div>
                ))}
              </div>
          }
        </div>

        {/* Peak Emission Events */}
        <div className="bg-white/5 rounded-xl p-5 border border-white/10">
          <h3 className="text-lg font-bold text-white mb-3">Top Emission Events</h3>
          {peakEvents.length === 0
            ? <p className="text-gray-400 text-sm">No peak events</p>
            : <div className="space-y-2">
                {peakEvents.slice(0, 6).map((e, i) => (
                  <div key={i} className="bg-orange-500/10 border-l-4 border-orange-500 rounded-lg p-3">
                    <div className="flex justify-between mb-1">
                      <span className="text-white text-sm font-medium">{e.region}</span>
                      <span className="text-orange-300 text-sm">{(e.emissions_kg ?? 0).toFixed(6)} kg</span>
                    </div>
                    <div className="flex justify-between text-xs text-gray-400">
                      <span>{e.time?.split('T')[0] ?? 'N/A'}</span>
                      <span>{e.carbon_intensity} gCO₂/kWh · ${(e.cost ?? 0).toFixed(4)}</span>
                    </div>
                  </div>
                ))}
              </div>
          }
        </div>
      </div>

      {/* Full Run History Table */}
      <div className="bg-white/5 rounded-xl p-5 border border-white/10">
        <h3 className="text-lg font-bold text-white mb-3">
          Daily Run History
          <span className="ml-2 text-sm font-normal text-gray-400">({timeline.length} records)</span>
        </h3>
        {timeline.length === 0
          ? <p className="text-gray-400 text-sm">No history data</p>
          : <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="border-b border-white/20 text-gray-400">
                    <th className="pb-2 pr-4">Date</th>
                    <th className="pb-2 pr-4">Region</th>
                    <th className="pb-2 pr-4">Usage Type</th>
                    <th className="pb-2 pr-4">Usage Amount</th>
                    <th className="pb-2 pr-4">Cost ($)</th>
                    <th className="pb-2 pr-4">Carbon Intensity</th>
                    <th className="pb-2 pr-4">Energy (kWh)</th>
                    <th className="pb-2">Emissions (kg)</th>
                  </tr>
                </thead>
                <tbody>
                  {timeline.map((row, i) => (
                    <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                      <td className="py-2 pr-4 text-gray-300">{row.timestamp?.split('T')[0] ?? '—'}</td>
                      <td className="py-2 pr-4 text-white">{row.region}</td>
                      <td className="py-2 pr-4 text-gray-400 text-xs">{row.usage_type || '—'}</td>
                      <td className="py-2 pr-4 text-gray-300">{(row.usage_amount ?? 0).toFixed(4)}</td>
                      <td className="py-2 pr-4 text-green-300">{(row.cost ?? 0).toFixed(4)}</td>
                      <td className="py-2 pr-4 text-yellow-300">{row.carbon_intensity} g/kWh</td>
                      <td className="py-2 pr-4 text-blue-300">{(row.energy_kwh ?? 0).toFixed(6)}</td>
                      <td className="py-2 text-red-300">{(row.emissions_kg ?? 0).toFixed(6)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
        }
      </div>

      {/* Optimization Recommendations */}
      {optimization.recommendations?.length > 0 && (
        <div className="bg-green-500/10 rounded-xl p-5 border border-green-500/30">
          <h3 className="text-lg font-bold text-green-300 mb-3">Optimization Recommendations</h3>
          {optimization.estimated_savings && (
            <div className="grid grid-cols-3 gap-4 mb-4 p-3 bg-green-500/20 rounded-lg text-center">
              <div>
                <div className="text-xl font-bold text-white">{(optimization.estimated_savings.emissions_reduction_kg ?? 0).toFixed(4)} kg</div>
                <div className="text-xs text-green-200">Potential CO₂ Reduction</div>
              </div>
              <div>
                <div className="text-xl font-bold text-white">${(optimization.estimated_savings.cost_reduction ?? 0).toFixed(4)}</div>
                <div className="text-xs text-green-200">Cost Savings</div>
              </div>
              <div>
                <div className="text-xl font-bold text-white">{optimization.estimated_savings.efficiency_gain_percentage ?? 0}%</div>
                <div className="text-xs text-green-200">Efficiency Gain</div>
              </div>
            </div>
          )}
          <div className="space-y-2">
            {optimization.recommendations.map((rec, i) => (
              <div key={i} className="bg-white/5 rounded-lg p-3 text-white text-sm">• {rec}</div>
            ))}
          </div>
        </div>
      )}

      {/* What-If Scenarios */}
      {whatif.length > 0 && (
        <div className="bg-purple-500/10 rounded-xl p-5 border border-purple-500/30">
          <h3 className="text-lg font-bold text-purple-300 mb-3">What-If Scenarios</h3>
          <div className="space-y-3">
            {whatif.map((s, i) => (
              <div key={i} className="bg-white/5 rounded-lg p-4">
                <div className="flex justify-between items-start mb-1">
                  <span className="text-white font-semibold">{s.title}</span>
                  <span className="text-purple-300 text-sm">-{s.potential_reduction_percentage}%</span>
                </div>
                <div className="text-xs text-gray-400">{s.current} → {s.alternative}</div>
                <div className="text-green-400 text-sm mt-1">Save {(s.potential_reduction_kg ?? 0).toFixed(4)} kg CO₂</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const SCard = ({ label, value, color, icon }) => {
  const colors = {
    red: 'bg-red-500/20 border-red-500/30 text-red-300',
    green: 'bg-green-500/20 border-green-500/30 text-green-300',
    blue: 'bg-blue-500/20 border-blue-500/30 text-blue-300',
    yellow: 'bg-yellow-500/20 border-yellow-500/30 text-yellow-300',
  };
  return (
    <div className={`rounded-lg p-4 border ${colors[color]}`}>
      <div className="flex items-center gap-2 mb-1 opacity-70">{icon}<span className="text-xs">{label}</span></div>
      <div className="text-xl font-bold text-white">{value}</div>
    </div>
  );
};

export default ServiceDetailDashboard;
