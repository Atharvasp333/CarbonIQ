import { useState, useEffect } from 'react';
import { simulateCloudUsage, uploadCustomCSV, getResultsHistory } from '../api/client';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function CloudSimulationPanel() {
  const [runtime, setRuntime] = useState(1);
  const [cpuUsage, setCpuUsage] = useState(50);
  const [region, setRegion] = useState('IN');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState('');
  
  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      const data = await getResultsHistory();
      setResults(data.reverse()); // Show newest first
    } catch (err) {
      console.error('Error fetching history:', err);
    }
  };

  const handleSimulate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await simulateCloudUsage({ runtime: parseFloat(runtime), cpu_utilization: parseFloat(cpuUsage), region });
      await fetchResults();
    } catch (err) {
      setError('Simulation failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      await uploadCustomCSV(file);
      await fetchResults();
    } catch (err) {
      setError('CSV upload failed. Please ensure columns are: runtime, cpu_usage, region');
    } finally {
      setLoading(false);
      e.target.value = null; // Reset input
    }
  };

  const latestResult = results.length > 0 ? results[0] : null;

  const chartData = results.slice(0, 5).map((r, i) => ({
    name: `Run ${i + 1}`,
    emissions: r.type === 'simulation' ? r.emissions_kg_co2e : r.total_emissions_kg_co2e
  })).reverse(); // Oldest of the newest first for left-to-right timeline

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-500/20 border border-red-500/50 p-4 rounded-xl text-red-200">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Simulation Form */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
          <h2 className="text-xl font-bold text-white mb-2">Cloud Workload Simulation</h2>
          <p className="text-slate-400 text-sm mb-6">Estimate carbon emissions based on server runtime and CPU usage. Assumes base capacity of 100W per server.</p>
          
          <form onSubmit={handleSimulate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Runtime (hours)</label>
              <input type="number" min="0.1" step="0.1" required value={runtime} onChange={e => setRuntime(e.target.value)}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">CPU Utilization (%)</label>
              <input type="number" min="1" max="100" required value={cpuUsage} onChange={e => setCpuUsage(e.target.value)}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Region</label>
              <select value={region} onChange={e => setRegion(e.target.value)}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500">
                <option value="IN">India (IN)</option>
                <option value="US">United States (US)</option>
              </select>
            </div>
            <button type="submit" disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition disabled:opacity-50">
              {loading ? 'Processing...' : 'Simulate Emissions'}
            </button>
          </form>

          <div className="mt-6 border-t border-slate-700 pt-4">
            <h3 className="text-lg font-semibold text-white mb-2">Batch CSV Upload</h3>
            <p className="text-slate-400 text-sm mb-4">Upload a CSV with headers: <code>runtime, cpu_usage, region</code></p>
            <input type="file" accept=".csv" onChange={handleFileUpload} disabled={loading}
              className="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer" />
          </div>
        </div>

        {/* Latest Results & Chart */}
        <div className="space-y-6">
          {latestResult && (
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-white mb-4">Latest Result</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                  <p className="text-sm text-slate-400 mb-1">Energy Consumed</p>
                  <p className="text-2xl font-bold text-blue-400">
                    {latestResult.type === 'simulation' ? latestResult.energy_kwh : latestResult.total_energy_kwh} <span className="text-sm font-normal text-slate-500">kWh</span>
                  </p>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                  <p className="text-sm text-slate-400 mb-1">Carbon Emissions</p>
                  <p className="text-2xl font-bold text-green-400">
                    {latestResult.type === 'simulation' ? latestResult.emissions_kg_co2e : latestResult.total_emissions_kg_co2e} <span className="text-sm font-normal text-slate-500">kg CO₂e</span>
                  </p>
                </div>
              </div>
              {latestResult.type === 'csv_upload' && (
                <p className="text-slate-400 text-sm mt-4 text-center">Aggregated from {latestResult.row_count} rows in {latestResult.filename}</p>
              )}
            </div>
          )}

          {results.length > 0 && (
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4">Recent History</h3>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
                    <YAxis stroke="#94a3b8" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
                      itemStyle={{ color: '#3b82f6' }}
                    />
                    <Bar dataKey="emissions" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* History Table */}
      {results.length > 0 && (
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-700">
            <h3 className="text-lg font-semibold text-white">Full History</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs text-slate-400 uppercase bg-slate-900/50">
                <tr>
                  <th className="px-6 py-3">Type</th>
                  <th className="px-6 py-3">Date</th>
                  <th className="px-6 py-3">Energy (kWh)</th>
                  <th className="px-6 py-3">Emissions (kg CO₂e)</th>
                  <th className="px-6 py-3">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {results.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-700/30">
                    <td className="px-6 py-4 font-medium text-white">
                      {item.type === 'simulation' ? 'Single Sim' : 'CSV Batch'}
                    </td>
                    <td className="px-6 py-4">{new Date(item.timestamp).toLocaleString()}</td>
                    <td className="px-6 py-4">{item.type === 'simulation' ? item.energy_kwh : item.total_energy_kwh}</td>
                    <td className="px-6 py-4">{item.type === 'simulation' ? item.emissions_kg_co2e : item.total_emissions_kg_co2e}</td>
                    <td className="px-6 py-4 text-slate-400 text-xs">
                      {item.type === 'simulation' ? `CPU: ${item.cpu_utilization}%, Time: ${item.runtime}h` : `Rows: ${item.row_count}`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default CloudSimulationPanel;
