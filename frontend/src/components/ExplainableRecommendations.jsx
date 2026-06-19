import { Lightbulb, TrendingDown, CheckCircle, AlertCircle, Info, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

export default function ExplainableRecommendations({ intelligence }) {
  if (!intelligence) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="text-center text-gray-500">
          <Info className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>Intelligence layer not available</p>
        </div>
      </div>
    );
  }

  const { recommendations, summary, insights } = intelligence;

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

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-xl shadow-lg p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <Lightbulb className="w-8 h-8" />
          <h2 className="text-2xl font-bold">Explainable Sustainability Recommendations</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
            <div className="text-sm opacity-90">Total Recommendations</div>
            <div className="text-3xl font-bold mt-1">{summary.total_recommendations}</div>
          </div>
          
          <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
            <div className="text-sm opacity-90">Potential Reduction</div>
            <div className="text-3xl font-bold mt-1">{summary.total_potential_reduction_kg?.toFixed(2)} kg</div>
            <div className="text-xs opacity-75 mt-1">CO₂ Savings</div>
          </div>
          
          <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
            <div className="text-sm opacity-90">High Priority</div>
            <div className="text-3xl font-bold mt-1">{summary.high_priority_count}</div>
            <div className="text-xs opacity-75 mt-1">Immediate Action</div>
          </div>
          
          <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
            <div className="text-sm opacity-90">Top Category</div>
            <div className="text-xl font-bold mt-2 capitalize">{summary.categories?.[0] || 'N/A'}</div>
          </div>
        </div>
      </div>

      {/* Insights Summary */}
      {insights && insights.length > 0 && (
        <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-6">
          <h3 className="text-lg font-bold text-blue-900 mb-3 flex items-center gap-2">
            <Info className="w-5 h-5" />
            Key Findings ({insights.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {insights.slice(0, 4).map((insight, idx) => (
              <div key={idx} className="bg-white rounded-lg p-4 border border-blue-200">
                <p className="text-sm font-semibold text-gray-800">{insight.observation}</p>
                <div className="mt-2 flex items-center justify-between">
                  <span className={`text-xs px-2 py-1 rounded-full font-bold ${
                    insight.severity === 'high' ? 'bg-red-100 text-red-800' : 
                    insight.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' : 
                    'bg-green-100 text-green-800'
                  }`}>
                    {insight.severity?.toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-500 capitalize">{insight.type?.replace('_', ' ')}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations List */}
      <div className="space-y-4">
        {recommendations.map((rec, idx) => (
          <ExplainableRecommendationCard key={idx} recommendation={rec} index={idx} />
        ))}
      </div>
    </div>
  );
}

function ExplainableRecommendationCard({ recommendation, index }) {
  const [expanded, setExpanded] = useState(index === 0); // First card expanded by default

  const getPriorityBadge = (priority) => {
    if (priority === 1) return { color: 'bg-red-100 text-red-800 border-red-300', label: 'PRIORITY 1' };
    if (priority === 2) return { color: 'bg-orange-100 text-orange-800 border-orange-300', label: 'PRIORITY 2' };
    if (priority === 3) return { color: 'bg-yellow-100 text-yellow-800 border-yellow-300', label: 'PRIORITY 3' };
    return { color: 'bg-gray-100 text-gray-800 border-gray-300', label: `PRIORITY ${priority}` };
  };

  const getCategoryColor = (category) => {
    const colors = {
      'scheduling': 'from-green-500 to-emerald-500',
      'service': 'from-blue-500 to-cyan-500',
      'resource': 'from-purple-500 to-pink-500',
      'cost': 'from-yellow-500 to-orange-500',
      'region': 'from-red-500 to-rose-500'
    };
    return colors[category] || 'from-gray-500 to-gray-600';
  };

  const getConfidenceBadge = (confidence) => {
    const styles = {
      High: 'bg-green-100 text-green-800 border-green-300',
      Medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      Low: 'bg-orange-100 text-orange-800 border-orange-300'
    };
    return styles[confidence] || styles.Medium;
  };

  const priorityBadge = getPriorityBadge(recommendation.priority);

  return (
    <div className={`bg-white rounded-xl shadow-lg border-l-4 ${
      recommendation.priority === 1 ? 'border-red-500' : 
      recommendation.priority === 2 ? 'border-orange-500' : 
      'border-blue-500'
    } overflow-hidden`}>
      {/* Header */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-3">
              <span className={`px-3 py-1 rounded-full text-xs font-bold border ${priorityBadge.color}`}>
                {priorityBadge.label}
              </span>
              <span className={`px-3 py-1 bg-gradient-to-r ${getCategoryColor(recommendation.category)} text-white rounded-full text-xs font-bold capitalize`}>
                {recommendation.category}
              </span>
              <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getConfidenceBadge(recommendation.confidence)}`}>
                {recommendation.confidence} Confidence
              </span>
            </div>
            <h3 className="text-xl font-bold text-gray-900">{recommendation.title}</h3>
            <p className="text-sm text-gray-600 mt-1">{recommendation.service}</p>
          </div>
          
          <div className="text-right ml-4">
            <div className="flex items-center gap-2 text-green-600">
              <TrendingDown className="w-6 h-6" />
              <span className="text-3xl font-bold">{recommendation.expected_reduction_kg?.toFixed(2)}</span>
            </div>
            <div className="text-sm text-gray-500 mt-1">{recommendation.expected_reduction_pct?.toFixed(1)}% reduction</div>
            <div className="text-xs text-gray-500 mt-1">Cost: {recommendation.cost_impact}</div>
          </div>
        </div>

        {/* Observation */}
        <div className="mb-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
          <h4 className="text-sm font-bold text-blue-900 mb-1">📊 Observation</h4>
          <p className="text-sm text-blue-800">{recommendation.observation}</p>
        </div>

        {/* Toggle Button */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-between px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
        >
          <span className="text-sm font-semibold text-gray-700">
            {expanded ? 'Hide Details' : 'Show Evidence & Implementation'}
          </span>
          {expanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div className="px-6 pb-6 space-y-4 border-t border-gray-200 pt-4">
          {/* Evidence */}
          <div className="p-4 bg-purple-50 border-l-4 border-purple-500 rounded">
            <h4 className="text-sm font-bold text-purple-900 mb-2">🔍 Evidence</h4>
            <div className="grid grid-cols-2 gap-3 text-sm">
              {Object.entries(recommendation.evidence || {}).map(([key, value]) => {
                if (key === 'data_source') return null;
                return (
                  <div key={key} className="bg-white rounded p-2">
                    <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}:</span>
                    <span className="ml-2 font-semibold text-gray-900">
                      {typeof value === 'number' ? value.toFixed(2) : 
                       Array.isArray(value) ? value.join(', ') : 
                       value}
                    </span>
                  </div>
                );
              })}
            </div>
            {recommendation.evidence?.data_source && (
              <p className="text-xs text-purple-700 mt-2">
                Source: {recommendation.evidence.data_source}
              </p>
            )}
          </div>

          {/* Root Cause */}
          <div className="p-4 bg-yellow-50 border-l-4 border-yellow-500 rounded">
            <h4 className="text-sm font-bold text-yellow-900 mb-1">🎯 Root Cause</h4>
            <p className="text-sm text-yellow-800">{recommendation.root_cause}</p>
          </div>

          {/* Explanation (if available from AI) */}
          {recommendation.explanation && (
            <div className="p-4 bg-green-50 border-l-4 border-green-500 rounded">
              <h4 className="text-sm font-bold text-green-900 mb-2">💡 Detailed Explanation</h4>
              <div className="text-sm text-green-800 whitespace-pre-line">
                {recommendation.explanation}
              </div>
              <p className="text-xs text-green-600 mt-2">
                Generated by: {recommendation.explanation_source === 'gemini' ? '🤖 Gemini AI' : '📝 Template'}
              </p>
            </div>
          )}

          {/* Expected Impact Summary */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
              <div className="text-xs text-green-700 mb-1">Carbon Reduction</div>
              <div className="text-2xl font-bold text-green-900">{recommendation.expected_reduction_kg?.toFixed(2)} kg</div>
              <div className="text-xs text-green-600 mt-1">{recommendation.expected_reduction_pct?.toFixed(1)}%</div>
            </div>
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg p-4 border border-blue-200">
              <div className="text-xs text-blue-700 mb-1">Cost Impact</div>
              <div className="text-xl font-bold text-blue-900">{recommendation.cost_impact}</div>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200">
              <div className="text-xs text-purple-700 mb-1">Complexity</div>
              <div className="text-xl font-bold text-purple-900">{recommendation.implementation_complexity || 'Medium'}</div>
            </div>
          </div>

          {/* Constraints Applied */}
          {recommendation.constraints_applied && recommendation.constraints_applied.length > 0 && (
            <div className="flex flex-wrap gap-2">
              <span className="text-sm font-semibold text-gray-700">Constraints Applied:</span>
              {recommendation.constraints_applied.map((constraint, i) => (
                <span key={i} className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-semibold">
                  {constraint}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
