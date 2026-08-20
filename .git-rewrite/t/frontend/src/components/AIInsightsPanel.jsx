function AIInsightsPanel({ insights }) {
  if (!insights) {
    return (
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
        <p className="text-slate-400">Loading insights...</p>
      </div>
    );
  }

  const priorityColors = {
    high: 'border-red-500/50 bg-red-500/10',
    medium: 'border-yellow-500/50 bg-yellow-500/10',
    low: 'border-blue-500/50 bg-blue-500/10'
  };

  const priorityBadges = {
    high: 'bg-red-500 text-white',
    medium: 'bg-yellow-500 text-black',
    low: 'bg-blue-500 text-white'
  };

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 backdrop-blur-sm rounded-xl p-6 border border-blue-500/30">
        <h3 className="text-xl font-semibold text-white mb-2">🤖 AI Analysis Summary</h3>
        <p className="text-slate-200">{insights.summary}</p>
      </div>

      {/* Carbon Budget Status */}
      {insights.carbon_budget_status && (
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
          <h3 className="text-lg font-semibold text-white mb-4">📊 Carbon Budget Status</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-slate-400 text-sm">Current Monthly</p>
              <p className="text-2xl font-bold text-white">
                {insights.carbon_budget_status.current_monthly_kg} kg
              </p>
            </div>
            <div>
              <p className="text-slate-400 text-sm">Recommended Target</p>
              <p className="text-2xl font-bold text-green-400">
                {insights.carbon_budget_status.recommended_target_kg} kg
              </p>
            </div>
            <div>
              <p className="text-slate-400 text-sm">Status</p>
              <p className={`text-2xl font-bold ${
                insights.carbon_budget_status.status === 'excellent' ? 'text-green-400' :
                insights.carbon_budget_status.status === 'on_track' ? 'text-yellow-400' :
                'text-red-400'
              }`}>
                {insights.carbon_budget_status.status.replace('_', ' ').toUpperCase()}
              </p>
            </div>
          </div>
          <div className="mt-4 bg-slate-700/50 rounded-full h-4 overflow-hidden">
            <div
              className={`h-full transition-all ${
                insights.carbon_budget_status.status === 'excellent' ? 'bg-green-500' :
                insights.carbon_budget_status.status === 'on_track' ? 'bg-yellow-500' :
                'bg-red-500'
              }`}
              style={{
                width: `${Math.min(
                  (insights.carbon_budget_status.current_monthly_kg /
                    insights.carbon_budget_status.recommended_target_kg) * 100,
                  100
                )}%`
              }}
            />
          </div>
        </div>
      )}

      {/* Recommendations */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
        <h3 className="text-lg font-semibold text-white mb-4">💡 Optimization Recommendations</h3>
        <div className="space-y-4">
          {insights.recommendations.map((rec, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-lg border ${priorityColors[rec.priority]}`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${priorityBadges[rec.priority]}`}>
                      {rec.priority.toUpperCase()}
                    </span>
                    <span className="text-slate-400 text-xs">
                      {rec.category}
                    </span>
                  </div>
                  <h4 className="text-white font-semibold">{rec.title}</h4>
                </div>
              </div>
              <p className="text-slate-300 text-sm mb-3">{rec.description}</p>
              <div className="flex gap-4 text-sm">
                <div className="flex items-center gap-1">
                  <span className="text-green-400">💰</span>
                  <span className="text-slate-300">Save: ${rec.estimated_savings_cost.toFixed(2)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-blue-400">🌍</span>
                  <span className="text-slate-300">Reduce: {rec.estimated_savings_kg.toFixed(2)} kg CO₂</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AIInsightsPanel;
