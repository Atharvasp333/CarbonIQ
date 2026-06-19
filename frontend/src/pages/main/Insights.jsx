import { useState, useEffect } from 'react';
import { Lightbulb, Upload, AlertCircle, TrendingDown } from 'lucide-react';
import ExplainableRecommendations from '../../components/ExplainableRecommendations';
import { Link } from 'react-router-dom';

export default function Insights() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalysisData();
  }, []);

  const loadAnalysisData = () => {
    try {
      const raw = localStorage.getItem('awsAnalysisData');
      if (raw) {
        const parsedData = JSON.parse(raw);
        setData(parsedData);
      }
    } catch (error) {
      console.error('Error loading analysis data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-green-500 border-t-transparent"></div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="text-center py-16">
          <div className="mb-6">
            <Lightbulb className="w-20 h-20 text-gray-300 mx-auto mb-4" />
            <h2 className="text-3xl font-bold text-gray-800 mb-2">No Analysis Data Available</h2>
            <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
              Upload your AWS Cost and Usage Report to receive personalized sustainability insights and recommendations powered by our intelligent agent system.
            </p>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-green-50 rounded-xl p-8 max-w-3xl mx-auto border-2 border-blue-200">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Get Started in 2 Steps:</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
              <div className="bg-white rounded-lg p-6 border-2 border-green-300">
                <div className="flex items-center mb-3">
                  <div className="bg-green-100 rounded-full w-8 h-8 flex items-center justify-center mr-3">
                    <span className="text-green-600 font-bold">1</span>
                  </div>
                  <h4 className="font-bold text-gray-800">Configure Profile</h4>
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  Set up your organization preferences to receive personalized recommendations.
                </p>
                <Link
                  to="/settings"
                  className="inline-block px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-semibold rounded-lg transition"
                >
                  Go to Settings
                </Link>
              </div>

              <div className="bg-white rounded-lg p-6 border-2 border-blue-300">
                <div className="flex items-center mb-3">
                  <div className="bg-blue-100 rounded-full w-8 h-8 flex items-center justify-center mr-3">
                    <span className="text-blue-600 font-bold">2</span>
                  </div>
                  <h4 className="font-bold text-gray-800">Upload CUR Data</h4>
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  Upload your AWS Cost and Usage Report for analysis.
                </p>
                <Link
                  to="/"
                  className="inline-block px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition"
                >
                  Upload CUR
                </Link>
              </div>
            </div>
          </div>

          <div className="mt-8 max-w-3xl mx-auto">
            <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-6">
              <div className="flex items-start">
                <AlertCircle className="w-6 h-6 text-yellow-600 mr-3 flex-shrink-0 mt-1" />
                <div className="text-left">
                  <h4 className="font-bold text-yellow-800 mb-2">What You'll Get:</h4>
                  <ul className="text-sm text-yellow-700 space-y-1">
                    <li>• Personalized sustainability recommendations</li>
                    <li>• Service-specific optimization opportunities (EC2, Lambda, S3, SageMaker)</li>
                    <li>• Region and time-shift suggestions</li>
                    <li>• Confidence-scored recommendations based on your constraints</li>
                    <li>• Carbon hotspot identification</li>
                    <li>• Potential emission reduction estimates</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Check if intelligence data is available
  const hasIntelligence = data.intelligence && data.intelligence.recommendations;

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <Lightbulb className="w-8 h-8 text-green-600" />
          <h1 className="text-4xl font-bold text-gray-900">Sustainability Insights</h1>
        </div>
        <p className="text-gray-600 text-lg">
          AI-powered recommendations to reduce your carbon footprint and optimize costs
        </p>
      </div>

      {/* Summary Banner */}
      {data.summary && (
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white shadow-xl">
          <h2 className="text-2xl font-bold mb-4">Current Analysis Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
              <div className="text-sm opacity-90">Total Emissions</div>
              <div className="text-3xl font-bold mt-1">{data.summary.total_emissions_kg?.toFixed(2)} kg</div>
              <div className="text-xs opacity-75 mt-1">CO₂ Emissions</div>
            </div>
            <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
              <div className="text-sm opacity-90">Total Cost</div>
              <div className="text-3xl font-bold mt-1">${data.summary.total_cost?.toFixed(2)}</div>
              <div className="text-xs opacity-75 mt-1">AWS Spend</div>
            </div>
            <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
              <div className="text-sm opacity-90">Top Service</div>
              <div className="text-xl font-bold mt-2">{data.summary.top_service || 'N/A'}</div>
            </div>
            <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
              <div className="text-sm opacity-90">Top Region</div>
              <div className="text-xl font-bold mt-2">{data.summary.top_region || 'N/A'}</div>
            </div>
          </div>
        </div>
      )}

      {/* Intelligence Layer Results */}
      {hasIntelligence ? (
        <ExplainableRecommendations intelligence={data.intelligence} />
      ) : (
        <div className="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-8">
          <div className="flex items-start">
            <AlertCircle className="w-12 h-12 text-yellow-600 mr-4 flex-shrink-0" />
            <div>
              <h3 className="text-2xl font-bold text-yellow-900 mb-2">Intelligence Layer Not Available</h3>
              <p className="text-yellow-800 mb-4">
                The sustainability intelligence layer was not included in this analysis. 
                This might be because:
              </p>
              <ul className="text-yellow-700 space-y-2 mb-6">
                <li className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>The data was uploaded before the intelligence layer was implemented</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>The intelligence layer was disabled during analysis</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>The backend server needs to be restarted to load the new agents</span>
                </li>
              </ul>
              
              <div className="space-y-3">
                <p className="font-semibold text-yellow-900">To get personalized recommendations:</p>
                <ol className="text-yellow-800 space-y-2">
                  <li className="flex items-start">
                    <span className="font-bold mr-2">1.</span>
                    <span>Make sure your backend server is running the latest code</span>
                  </li>
                  <li className="flex items-start">
                    <span className="font-bold mr-2">2.</span>
                    <span>Configure your organization profile in Settings</span>
                  </li>
                  <li className="flex items-start">
                    <span className="font-bold mr-2">3.</span>
                    <span>Upload your CUR file again</span>
                  </li>
                </ol>
              </div>

              <div className="mt-6 flex gap-4">
                <Link
                  to="/settings"
                  className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition"
                >
                  Configure Profile
                </Link>
                <Link
                  to="/"
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition"
                >
                  Upload New CUR
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Basic Optimization (from old system) */}
      {data.optimization && data.optimization.opportunities && data.optimization.opportunities.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <TrendingDown className="w-6 h-6 text-orange-600" />
            <h2 className="text-2xl font-bold text-gray-900">Legacy Optimization Opportunities</h2>
          </div>
          <p className="text-gray-600 mb-4">
            Basic optimization suggestions from the original system (not constraint-aware)
          </p>
          
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-orange-900">{data.optimization.reduction_estimates.total_potential_reduction_kg.toFixed(2)} kg</div>
                <div className="text-sm text-orange-700">Potential Reduction</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-orange-900">${data.optimization.reduction_estimates.total_potential_cost_savings.toFixed(2)}</div>
                <div className="text-sm text-orange-700">Cost Savings</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-orange-900">{data.optimization.reduction_estimates.percentage_reduction.toFixed(1)}%</div>
                <div className="text-sm text-orange-700">Reduction %</div>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            {data.optimization.opportunities.slice(0, 10).map((opp, idx) => (
              <div key={idx} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <span className="font-semibold text-gray-900 capitalize">{opp.type?.replace('_', ' ')}</span>
                    <p className="text-sm text-gray-600 mt-1">{opp.description}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    opp.priority === 'high' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {opp.priority?.toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
