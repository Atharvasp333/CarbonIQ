import { Lightbulb, TrendingDown, DollarSign, CheckCircle, AlertCircle, Info } from 'lucide-react';

export default function SustainabilityRecommendations({ intelligence }) {
  if (!intelligence) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="text-center text-gray-500">
          <Info className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>Intelligence layer not available</p>
          <p className="text-sm mt-1">Enable intelligence layer to see personalized recommendations</p>
        </div>
      </div>
    );
  }

  const { recommendations, summary, workload_analysis } = intelligence;

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="text-center text-gray-500">
          <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
          <p className="font-semibold">No optimization opportunities found</p>
          <p className="text-sm mt-1">Your infrastructure is already well-optimized!</p>
        </div>
      </div>
    );
  }

  const getConfidenceBadge = (confidence) => {
    const styles = {
      High: 'bg-green-100 text-green-800 border-green-300',
      Medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      Low: 'bg-orange-100 text-orange-800 border-orange-300'
    };
    return styles[confidence] || styles.Medium;
  };

  const getCostImpactIcon = (impact) => {
    if (impact === 'Positive') return <DollarSign className="w-4 h-4 text-green-600" />;
    if (impact === 'Negative') return <DollarSign className="w-4 h-4 text-red-600" />;
    return <DollarSign className="w-4 h-4 text-gray-600" />;
  };

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-xl shadow-lg p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <Lightbulb className="w-8 h-8" />
          <h2 className="text-2xl font-bold">Sustainability Recommendations</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
            <div className="text-sm opacity-90">Total Recommendations</div>
            <div className="text-3xl font-bold mt-1">{summary.total_recommendations}</div>
          </div>
          
          <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
            <div className="text-sm opacity-90">Potential Reduction</div>
            <div className="text-3xl font-bold mt-1">{summary.total_potential_reduction_kg?.toFixed(1)} kg</div>
            <div className="text-xs opacity-75 mt-1">{summary.total_potential_reduction_pct?.toFixed(1)}%</div>
          </div>
          
          <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
            <div className="text-sm opacity-90">High Confidence</div>
            <div className="text-3xl font-bold mt-1">{summary.high_confidence_count}</div>
          </div>
          
          <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
            <div className="text-sm opacity-90">Top Category</div>
            <div className="text-xl font-bold mt-2">{summary.top_category || 'N/A'}</div>
          </div>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {recommendations.map((rec, idx) => (
          <div key={rec.id || idx} className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500 hover:shadow-xl transition">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                    {rec.category}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getConfidenceBadge(rec.confidence)}`}>
                    {rec.confidence} Confidence
                  </span>
                </div>
                <h3 className="text-lg font-bold text-gray-800">{rec.title}</h3>
                <p className="text-sm text-gray-600 mt-1">{rec.service}</p>
              </div>
              
              <div className="text-right">
                <div className="flex items-center gap-1 text-green-600">
                  <TrendingDown className="w-5 h-5" />
                  <span className="text-2xl font-bold">{rec.carbon_reduction_kg?.toFixed(1)} kg</span>
                </div>
                <div className="text-sm text-gray-500 mt-1">{rec.carbon_reduction_pct?.toFixed(1)}% reduction</div>
                <div className="flex items-center justify-end gap-1 mt-2">
                  {getCostImpactIcon(rec.cost_impact)}
                  <span className="text-xs text-gray-600">{rec.cost_impact} Cost Impact</span>
                </div>
              </div>
            </div>

            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-700">{rec.reasoning}</p>
              
              {rec.constraints && rec.constraints.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {rec.constraints.map((constraint, i) => (
                    <span key={i} className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">
                      {constraint}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Additional Details */}
            {rec.details && Object.keys(rec.details).length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <details className="text-sm text-gray-600">
                  <summary className="cursor-pointer font-semibold hover:text-gray-800">
                    View Details
                  </summary>
                  <div className="mt-2 space-y-1">
                    {rec.details.current_region && (
                      <div>Current Region: <span className="font-mono">{rec.details.current_region}</span></div>
                    )}
                    {rec.details.suggested_region && (
                      <div>Suggested Region: <span className="font-mono">{rec.details.suggested_region}</span></div>
                    )}
                    {rec.details.current_intensity && (
                      <div>Current Intensity: <span className="font-mono">{rec.details.current_intensity} gCO2/kWh</span></div>
                    )}
                    {rec.details.suggested_intensity && (
                      <div>Suggested Intensity: <span className="font-mono">{rec.details.suggested_intensity} gCO2/kWh</span></div>
                    )}
                  </div>
                </details>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Hotspots Section */}
      {workload_analysis?.hotspots && workload_analysis.hotspots.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-6 h-6 text-red-500" />
            <h3 className="text-xl font-bold text-gray-800">Top Carbon Hotspots</h3>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left">Service</th>
                  <th className="px-4 py-2 text-left">Region</th>
                  <th className="px-4 py-2 text-left">Timestamp</th>
                  <th className="px-4 py-2 text-right">Emissions (kg CO2)</th>
                </tr>
              </thead>
              <tbody>
                {workload_analysis.hotspots.slice(0, 5).map((hotspot, idx) => (
                  <tr key={idx} className="border-t hover:bg-gray-50">
                    <td className="px-4 py-2 font-medium">{hotspot.service}</td>
                    <td className="px-4 py-2 font-mono text-xs">{hotspot.region}</td>
                    <td className="px-4 py-2 text-xs">{new Date(hotspot.timestamp).toLocaleString()}</td>
                    <td className="px-4 py-2 text-right font-semibold text-red-600">
                      {hotspot.emissions_kg?.toFixed(2)}
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
