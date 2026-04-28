import { useState } from 'react';
import { simulateWhatIf } from '../api/client';

function WhatIfSimulator({ awsData }) {
  const [scenario, setScenario] = useState('move_region');
  const [targetRegion, setTargetRegion] = useState('us-west-1');
  const [targetInstance, setTargetInstance] = useState('t3.medium');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const data = await simulateWhatIf({
        scenario,
        target_region: targetRegion,
        target_instance: targetInstance
      });
      setResult(data);
    } catch (error) {
      console.error('Simulation error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
        <h3 className="text-xl font-semibold text-white mb-4">🔮 What-If Scenario Simulator</h3>
        <p className="text-slate-400 mb-6">
          Explore how different optimization strategies would impact your carbon footprint
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-slate-300 mb-2">Select Scenario</label>
            <select
              value={scenario}
              onChange={(e) => setScenario(e.target.value)}
              className="w-full bg-slate-700 text-white rounded-lg px-4 py-2 border border-slate-600 focus:border-blue-500 focus:outline-none"
            >
              <option value="move_region">Move to Low-Carbon Region</option>
              <option value="downsize_instance">Downsize Instances</option>
              <option value="remove_idle">Remove Idle Resources</option>
            </select>
          </div>

          {scenario === 'move_region' && (
            <div>
              <label className="block text-slate-300 mb-2">Target Region</label>
              <select
                value={targetRegion}
                onChange={(e) => setTargetRegion(e.target.value)}
                className="w-full bg-slate-700 text-white rounded-lg px-4 py-2 border border-slate-600 focus:border-blue-500 focus:outline-none"
              >
                <option value="us-west-1">us-west-1 (California - Low Carbon)</option>
                <option value="us-west-2">us-west-2 (Oregon - Low Carbon)</option>
                <option value="eu-west-1">eu-west-1 (Ireland - Low Carbon)</option>
              </select>
            </div>
          )}

          {scenario === 'downsize_instance' && (
            <div>
              <label className="block text-slate-300 mb-2">Target Instance Type</label>
              <select
                value={targetInstance}
                onChange={(e) => setTargetInstance(e.target.value)}
                className="w-full bg-slate-700 text-white rounded-lg px-4 py-2 border border-slate-600 focus:border-blue-500 focus:outline-none"
              >
                <option value="t3.micro">t3.micro</option>
                <option value="t3.small">t3.small</option>
                <option value="t3.medium">t3.medium</option>
                <option value="t3.large">t3.large</option>
              </select>
            </div>
          )}

          <button
            onClick={handleSimulate}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50"
          >
            {loading ? 'Simulating...' : 'Run Simulation'}
          </button>
        </div>
      </div>

      {result && (
        <div className="bg-gradient-to-br from-green-500/20 to-blue-500/20 backdrop-blur-sm rounded-xl p-6 border border-green-500/30">
          <h3 className="text-xl font-semibold text-white mb-4">📊 Simulation Results</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div className="bg-slate-800/50 rounded-lg p-4">
              <p className="text-slate-400 text-sm">Current Emissions</p>
              <p className="text-3xl font-bold text-white">{result.current_co2_kg} kg</p>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-4">
              <p className="text-slate-400 text-sm">Projected Emissions</p>
              <p className="text-3xl font-bold text-green-400">{result.projected_co2_kg} kg</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div className="bg-slate-800/50 rounded-lg p-4">
              <p className="text-slate-400 text-sm">CO₂ Savings</p>
              <p className="text-2xl font-bold text-green-400">-{result.savings_kg} kg</p>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-4">
              <p className="text-slate-400 text-sm">Cost Savings</p>
              <p className="text-2xl font-bold text-green-400">${result.savings_cost}</p>
            </div>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-4">
            <p className="text-white">{result.description}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default WhatIfSimulator;
