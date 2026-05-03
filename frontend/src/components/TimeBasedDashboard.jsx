import { useState } from 'react';
import { Line, Bar, Pie } from 'recharts';
import { LineChart, BarChart, PieChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'];

function TimeBasedDashboard({ data, onBack }) {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">Time-Based Carbon Analysis</h1>
              <p className="text-slate-400 text-sm">Historical Emissions with Electricity Maps</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={onBack}
                className="px-4 py-2 rounded-lg bg-slate-700 text-slate-300 hover:bg-slate-600 transition"
              >
                ← Back
              </button>
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-4 py-2 rounded-lg transition ${
                  activeTab === 'overview'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('timeline')}
                className={`px-4 py-2 rounded-lg transition ${
                  activeTab === 'timeline'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                Timeline
              </button>
              <button
                onClick={() => setActiveTab('details')}
                className={`px-4 py-2 rounded-lg transition ${
                  activeTab === 'details'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                Details
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-700">
            <div className="text-slate-400 text-sm mb-1">Total CO₂</div>
            <div className="text-2xl font-bold text-white">{data.total_co2_kg} kg</div>
            <div className="text-xs text-slate-500 mt-1">{data.total_energy_kwh.toFixed(2)} kWh</div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-700">
            <div className="text-slate-400 text-sm mb-1">Total Cost</div>
            <div className="text-2xl font-bold text-white">${data.total_cost}</div>
            <div className="text-xs text-slate-500 mt-1">{data.processed_rows} rows processed</div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-700">
            <div className="text-slate-400 text-sm mb-1">Top Region</div>
            <div className="text-2xl font-bold text-white">{data.top_region}</div>
            <div className="text-xs text-slate-500 mt-1">Highest emissions</div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-700">
            <div className="text-slate-400 text-sm mb-1">Top Service</div>
            <div className="text-2xl font-bold text-white">{data.top_service}</div>
            <div className="text-xs text-slate-500 mt-1">Highest emissions</div>
          </div>
        </div>

        {/* API Stats */}
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-blue-400 mb-1">⚡ Electricity Maps API Usage</h3>
              <p className="text-xs text-slate-300">
                API Calls: {data.api_calls} | Cached: {data.cached_calls} | Fallback: {data.fallback_calls} | Cache Size: {data.cache_size}
              </p>
            </div>
            <div className="text-right">
              <div className="text-xs text-slate-400">Efficiency</div>
              <div className="text-lg font-bold text-blue-400">
                {data.processed_rows > 0 ? Math.round((data.cached_calls / data.processed_rows) * 100) : 0}%
              </div>
            </div>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Emissions by Service */}
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4">Emissions by Service</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={data.by_service}
                      dataKey="co2_kg"
                      nameKey="service"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      label={(entry) => `${entry.service}: ${entry.co2_kg.toFixed(2)} kg`}
                    >
                      {data.by_service.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Emissions by Region */}
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4">Emissions by Region</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={data.by_region}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="region" stroke="#9CA3AF" />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                      labelStyle={{ color: '#F3F4F6' }}
                    />
                    <Bar dataKey="co2_kg" fill="#3B82F6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Region Details Table */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4">Region Details</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left py-3 px-4 text-slate-300">Region</th>
                      <th className="text-left py-3 px-4 text-slate-300">Zone</th>
                      <th className="text-right py-3 px-4 text-slate-300">CO₂ (kg)</th>
                      <th className="text-right py-3 px-4 text-slate-300">Energy (kWh)</th>
                      <th className="text-right py-3 px-4 text-slate-300">Avg Intensity (gCO₂/kWh)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.by_region.map((region, idx) => (
                      <tr key={idx} className="border-b border-slate-700/50">
                        <td className="py-3 px-4 text-white">{region.region}</td>
                        <td className="py-3 px-4 text-slate-400">{region.zone}</td>
                        <td className="py-3 px-4 text-right text-white">{region.co2_kg.toFixed(4)}</td>
                        <td className="py-3 px-4 text-right text-slate-400">{region.energy_kwh.toFixed(4)}</td>
                        <td className="py-3 px-4 text-right text-blue-400">{region.avg_carbon_intensity}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'timeline' && (
          <div className="space-y-6">
            {/* Emissions Over Time */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4">Emissions Over Time</h3>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={data.by_time}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis 
                    dataKey="timestamp" 
                    stroke="#9CA3AF"
                    angle={-45}
                    textAnchor="end"
                    height={100}
                  />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                    labelStyle={{ color: '#F3F4F6' }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="co2_kg" stroke="#3B82F6" name="CO₂ (kg)" strokeWidth={2} />
                  <Line type="monotone" dataKey="avg_carbon_intensity" stroke="#10B981" name="Avg Intensity (gCO₂/kWh)" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Time Period Details */}
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4">Time Period Details</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left py-3 px-4 text-slate-300">Timestamp</th>
                      <th className="text-right py-3 px-4 text-slate-300">CO₂ (kg)</th>
                      <th className="text-right py-3 px-4 text-slate-300">Energy (kWh)</th>
                      <th className="text-right py-3 px-4 text-slate-300">Avg Intensity (gCO₂/kWh)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.by_time.map((time, idx) => (
                      <tr key={idx} className="border-b border-slate-700/50">
                        <td className="py-3 px-4 text-white">{time.timestamp}</td>
                        <td className="py-3 px-4 text-right text-white">{time.co2_kg.toFixed(4)}</td>
                        <td className="py-3 px-4 text-right text-slate-400">{time.energy_kwh.toFixed(4)}</td>
                        <td className="py-3 px-4 text-right text-blue-400">{time.avg_carbon_intensity}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'details' && (
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
            <h3 className="text-lg font-semibold text-white mb-4">Detailed Line Items</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-slate-300">Service</th>
                    <th className="text-left py-3 px-4 text-slate-300">Region</th>
                    <th className="text-left py-3 px-4 text-slate-300">Timestamp</th>
                    <th className="text-right py-3 px-4 text-slate-300">Usage</th>
                    <th className="text-right py-3 px-4 text-slate-300">Intensity</th>
                    <th className="text-right py-3 px-4 text-slate-300">CO₂ (kg)</th>
                    <th className="text-center py-3 px-4 text-slate-300">Source</th>
                  </tr>
                </thead>
                <tbody>
                  {data.line_items.map((item, idx) => (
                    <tr key={idx} className="border-b border-slate-700/50">
                      <td className="py-3 px-4 text-white">{item.service}</td>
                      <td className="py-3 px-4 text-slate-400">{item.region}</td>
                      <td className="py-3 px-4 text-slate-400 text-xs">{item.timestamp}</td>
                      <td className="py-3 px-4 text-right text-white">{item.usage_amount.toFixed(2)}</td>
                      <td className="py-3 px-4 text-right text-blue-400">{item.carbon_intensity}</td>
                      <td className="py-3 px-4 text-right text-white">{item.co2_kg.toFixed(6)}</td>
                      <td className="py-3 px-4 text-center">
                        {item.source === 'electricity_maps' && (
                          <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs">API</span>
                        )}
                        {item.source === 'electricity_maps_cached' && (
                          <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">Cached</span>
                        )}
                        {item.source === 'fallback' && (
                          <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded text-xs">Fallback</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {data.skipped_rows > 0 && (
              <p className="mt-4 text-sm text-yellow-400">
                ⚠️ {data.skipped_rows} rows were skipped due to missing or invalid data
              </p>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default TimeBasedDashboard;
