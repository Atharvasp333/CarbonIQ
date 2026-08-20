import { useState, useEffect } from 'react';
import { 
  Lightbulb, AlertCircle, Sparkles, CheckCircle, Info, 
  Settings, Clock, TrendingUp, Target, ChevronRight, Filter,
  Loader2, AlertTriangle, Eye
} from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../../api/client';

export default function Insights() {
  const [analysisData, setAnalysisData] = useState(null);
  const [profile, setProfile] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState('');
  const [error, setError] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState('All');
  const [selectedConfidence, setSelectedConfidence] = useState('All');
  const [expandedModal, setExpandedModal] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load analysis data from localStorage
      const raw = localStorage.getItem('awsAnalysisData');
      if (raw) {
        const parsedData = JSON.parse(raw);
        setAnalysisData(parsedData);
        
        // If intelligence data exists in analysis, use it immediately
        if (parsedData?.intelligence?.recommendations) {
          setRecommendations({
            recommendations: parsedData.intelligence.recommendations || [],
            patterns: parsedData.intelligence.patterns || [],
            opportunities: parsedData.intelligence.opportunities || [],
            summary: parsedData.intelligence.summary || {},
            workload_analysis: parsedData.intelligence.workload_analysis || {},
            generated_at: new Date().toISOString()
          });
        }
      }

      // Load organization profile
      try {
        const profileRes = await api.get('/api/profile');
        setProfile(profileRes.data);
      } catch (err) {
        console.log('No profile found');
      }
      
      // Try to load existing recommendations from backend (optional)
      try {
        const recsRes = await api.get('/api/intelligence/recommendations');
        // Only override if we got valid data from backend
        if (recsRes.data?.recommendations?.length > 0) {
          setRecommendations(recsRes.data);
        }
      } catch (err) {
        // 404 is expected if no recommendations exist yet
        if (err.response?.status !== 404) {
          console.error('Error loading recommendations:', err);
        }
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateInsights = async () => {
    setGenerating(true);
    setError(null);
    
    const progressMessages = [
      'Loading Analysis Summary...',
      'Running Workload Analysis...',
      'Detecting Patterns...',
      'Finding Optimization Opportunities...',
      'Validating Constraints...',
      'Generating Recommendations...',
      'Preparing Explanations...'
    ];
    
    let messageIndex = 0;
    const progressInterval = setInterval(() => {
      if (messageIndex < progressMessages.length) {
        setGenerationProgress(progressMessages[messageIndex]);
        messageIndex++;
      }
    }, 2000);

    try {
      // Call the backend intelligence generation endpoint
      const response = await api.post('/api/intelligence/generate-insights');
      
      clearInterval(progressInterval);
      
      // After generation, try to load the recommendations
      try {
        const recsRes = await api.get('/api/intelligence/recommendations');
        setRecommendations(recsRes.data);
        setGenerationProgress('Insights Generated');
      } catch (fetchErr) {
        // If backend doesn't have stored recommendations yet,
        // fall back to intelligence data from current analysis
        if (analysisData?.intelligence?.recommendations) {
          setRecommendations({
            recommendations: analysisData.intelligence.recommendations || [],
            patterns: analysisData.intelligence.patterns || [],
            opportunities: analysisData.intelligence.opportunities || [],
            summary: analysisData.intelligence.summary || {},
            workload_analysis: analysisData.intelligence.workload_analysis || {},
            generated_at: new Date().toISOString()
          });
          setGenerationProgress('Insights Generated');
        } else {
          throw new Error('Intelligence data not available. Please re-upload your CUR file with intelligence layer enabled.');
        }
      }
      
    } catch (err) {
      clearInterval(progressInterval);
      setError(err.response?.data?.detail || err.message || 'Failed to generate insights');
      setGenerationProgress('');
    } finally {
      setGenerating(false);
    }
  };

  const getFilteredRecommendations = () => {
    if (!recommendations?.recommendations) return [];
    
    let filtered = recommendations.recommendations;
    
    if (selectedFilter !== 'All') {
      filtered = filtered.filter(rec => rec.category === selectedFilter.toLowerCase());
    }
    
    if (selectedConfidence !== 'All') {
      filtered = filtered.filter(rec => rec.confidence === selectedConfidence);
    }
    
    return filtered;
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-12 h-12 text-green-500 animate-spin" />
        </div>
      </div>
    );
  }

  // Empty state - no analysis data
  if (!analysisData) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="text-center py-16">
          <Lightbulb className="w-20 h-20 text-gray-300 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-gray-800 mb-2">No Analysis Data Available</h2>
          <p className="text-gray-600 mb-4 max-w-2xl mx-auto">
            To generate sustainability insights, you first need to upload your AWS Cost and Usage Report (CUR) data.
          </p>
          <p className="text-gray-500 mb-8 max-w-2xl mx-auto text-sm">
            The insights engine analyzes your CUR data to identify patterns, detect optimization opportunities, and generate personalized carbon reduction recommendations.
          </p>
          <Link
            to="/"
            className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition"
          >
            Upload CUR Data Now
          </Link>
        </div>
      </div>
    );
  }

  const filteredRecommendations = getFilteredRecommendations();
  const categories = ['All', 'Scheduling', 'Compute', 'Storage', 'Database', 'Region', 'Cost'];

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <Sparkles className="w-9 h-9 text-green-600" />
          <h1 className="text-4xl font-bold text-gray-900">Sustainability Intelligence</h1>
        </div>
        <p className="text-gray-600 text-lg">
          Analyze operational patterns and generate personalized carbon reduction recommendations using workload data, organization constraints, and carbon-intensity intelligence.
        </p>
      </div>

      {/* Latest Analysis Status */}
      <div className="bg-white rounded-xl shadow-md p-6 border-2 border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Clock className="w-6 h-6 text-blue-600" />
            Latest Analysis
          </h2>
          <span className="text-sm text-gray-500">
            {new Date().toLocaleDateString()}
          </span>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="text-sm text-blue-700 mb-1">Total Emissions</div>
            <div className="text-2xl font-bold text-blue-900">
              {analysisData.summary?.total_emissions_kg?.toFixed(2) || '0'} kg
            </div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="text-sm text-purple-700 mb-1">Top Service</div>
            <div className="text-lg font-bold text-purple-900">
              {analysisData.summary?.top_service || 'N/A'}
            </div>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <div className="text-sm text-green-700 mb-1">Top Region</div>
            <div className="text-lg font-bold text-green-900">
              {analysisData.summary?.top_region || 'N/A'}
            </div>
          </div>
          <div className="bg-orange-50 rounded-lg p-4">
            <div className="text-sm text-orange-700 mb-1">Total Records</div>
            <div className="text-2xl font-bold text-orange-900">
              {analysisData.summary?.total_records || '0'}
            </div>
          </div>
          <div className="bg-indigo-50 rounded-lg p-4">
            <div className="text-sm text-indigo-700 mb-1">Analysis Date</div>
            <div className="text-sm font-bold text-indigo-900">
              {new Date().toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>

      {/* Organization Profile Status */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl shadow-md p-6 border-2 border-blue-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Settings className="w-6 h-6 text-purple-600" />
            Organization Profile
          </h2>
          <Link
            to="/settings"
            className="px-4 py-2 bg-white hover:bg-gray-50 text-purple-700 font-semibold rounded-lg border-2 border-purple-300 transition text-sm"
          >
            Edit Profile
          </Link>
        </div>
        
        {profile ? (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-white rounded-lg p-3 border border-blue-200">
              <div className="text-xs text-gray-600 mb-1">Primary Region</div>
              <div className="text-sm font-bold text-gray-900">{profile.primary_user_region}</div>
            </div>
            <div className="bg-white rounded-lg p-3 border border-blue-200">
              <div className="text-xs text-gray-600 mb-1">Workload Type</div>
              <div className="text-sm font-bold text-gray-900">{profile.workload_type}</div>
            </div>
            <div className="bg-white rounded-lg p-3 border border-blue-200">
              <div className="text-xs text-gray-600 mb-1">Latency</div>
              <div className="text-sm font-bold text-gray-900">{profile.latency_sensitivity}</div>
            </div>
            <div className="bg-white rounded-lg p-3 border border-blue-200">
              <div className="text-xs text-gray-600 mb-1">Migration</div>
              <div className="text-sm font-bold text-gray-900">{profile.migration_flexibility}</div>
            </div>
            <div className="bg-white rounded-lg p-3 border border-blue-200">
              <div className="text-xs text-gray-600 mb-1">Priority</div>
              <div className="text-sm font-bold text-gray-900">{profile.optimization_priority}</div>
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-yellow-900">Profile Incomplete</p>
                <p className="text-sm text-yellow-800 mt-1">
                  Complete your organization profile to improve recommendation quality.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Action Section */}
      {!recommendations && (
        <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-xl shadow-lg p-8 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">Ready to Generate Insights</h2>
              <p className="text-blue-50">
                Click below to analyze your workload patterns and generate personalized recommendations.
              </p>
            </div>
            <button
              onClick={handleGenerateInsights}
              disabled={generating || !analysisData}
              className={`px-8 py-4 rounded-lg font-bold text-lg transition flex items-center gap-3 ${
                generating || !analysisData
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-white text-green-600 hover:bg-green-50'
              }`}
            >
              {generating ? (
                <>
                  <Loader2 className="w-6 h-6 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-6 h-6" />
                  Generate Insights
                </>
              )}
            </button>
          </div>
          
          {generating && (
            <div className="mt-6 bg-white/20 rounded-lg p-4 backdrop-blur">
              <div className="flex items-center gap-3">
                <Loader2 className="w-5 h-5 animate-spin" />
                <span className="font-semibold">{generationProgress}</span>
              </div>
            </div>
          )}
          
          {error && (
            <div className="mt-6 bg-red-500 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">Generation Failed</p>
                  <p className="text-sm mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Success State - Show Insights Generated */}
      {recommendations && (
        <div className="bg-green-50 border-2 border-green-300 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-8 h-8 text-green-600" />
              <div>
                <h3 className="text-xl font-bold text-green-900">Insights Generated</h3>
                <p className="text-sm text-green-700">
                  {recommendations.generated_at && new Date(recommendations.generated_at).toLocaleString()}
                </p>
              </div>
            </div>
            <button
              onClick={handleGenerateInsights}
              disabled={generating}
              className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition"
            >
              Regenerate
            </button>
          </div>
        </div>
      )}

      {/* Detected Patterns Section */}
      {recommendations?.patterns && recommendations.patterns.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-purple-200">
          <div className="flex items-center gap-2 mb-4">
            <Eye className="w-6 h-6 text-purple-600" />
            <h2 className="text-2xl font-bold text-gray-900">Detected Patterns</h2>
          </div>
          <p className="text-gray-600 mb-6">
            Identified patterns that explain why recommendations exist
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.patterns.map((pattern, idx) => (
              <div key={idx} className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-5 border-2 border-purple-200">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-bold text-purple-900 text-lg">{pattern.pattern_type?.replace('_', ' ')}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    pattern.severity === 'high' ? 'bg-red-100 text-red-800' :
                    pattern.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {pattern.severity?.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-purple-800 mb-3">{pattern.description}</p>
                {pattern.affected_services && (
                  <div className="text-xs text-purple-700">
                    <span className="font-semibold">Affected: </span>
                    {pattern.affected_services.join(', ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Optimization Opportunities Section */}
      {recommendations?.opportunities && recommendations.opportunities.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-blue-200">
          <div className="flex items-center gap-2 mb-4">
            <Target className="w-6 h-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-900">Optimization Opportunities</h2>
          </div>
          <p className="text-gray-600 mb-6">
            Identified opportunities for carbon and cost optimization
          </p>
          
          <div className="space-y-3">
            {recommendations.opportunities.map((opp, idx) => (
              <div key={idx} className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg p-5 border border-blue-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-3 py-1 bg-blue-600 text-white rounded-full text-xs font-bold">
                        {opp.opportunity_type}
                      </span>
                      {opp.service && (
                        <span className="text-sm text-gray-600">{opp.service}</span>
                      )}
                    </div>
                    <h3 className="font-bold text-blue-900 mb-2">{opp.title}</h3>
                    <p className="text-sm text-blue-800">{opp.description}</p>
                  </div>
                  {opp.potential_reduction_kg && (
                    <div className="text-right ml-4">
                      <div className="text-2xl font-bold text-green-600">
                        {opp.potential_reduction_kg.toFixed(2)} kg
                      </div>
                      <div className="text-xs text-gray-500">Potential Reduction</div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters for Recommendations */}
      {recommendations?.recommendations && recommendations.recommendations.length > 0 && (
        <>
          <div className="bg-white rounded-xl shadow-md p-6 border-2 border-gray-200">
            <div className="flex items-center gap-2 mb-4">
              <Filter className="w-6 h-6 text-gray-600" />
              <h3 className="text-lg font-bold text-gray-900">Filter Recommendations</h3>
            </div>
            
            <div className="flex flex-wrap gap-3 mb-4">
              <span className="text-sm font-semibold text-gray-700">Category:</span>
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedFilter(cat)}
                  className={`px-4 py-2 rounded-lg text-sm font-semibold transition ${
                    selectedFilter === cat
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
            
            <div className="flex flex-wrap gap-3">
              <span className="text-sm font-semibold text-gray-700">Confidence:</span>
              {['All', 'High', 'Medium', 'Low'].map((conf) => (
                <button
                  key={conf}
                  onClick={() => setSelectedConfidence(conf)}
                  className={`px-4 py-2 rounded-lg text-sm font-semibold transition ${
                    selectedConfidence === conf
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {conf}
                </button>
              ))}
            </div>
          </div>

          {/* Validated Recommendations Section */}
          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-green-200">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-6 h-6 text-green-600" />
              <h2 className="text-2xl font-bold text-gray-900">Validated Recommendations</h2>
              <span className="ml-auto text-sm text-gray-600">
                {filteredRecommendations.length} of {recommendations.recommendations.length}
              </span>
            </div>
            <p className="text-gray-600 mb-6">
              Constraint-validated recommendations ready for implementation
            </p>
            
            {filteredRecommendations.length === 0 ? (
              <div className="text-center py-8">
                <Info className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">No recommendations match the selected filters</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredRecommendations.map((rec, idx) => (
                  <RecommendationCard 
                    key={idx} 
                    recommendation={rec} 
                    onExpand={() => setExpandedModal(rec)}
                  />
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {/* Recommendation Detail Modal */}
      {expandedModal && (
        <RecommendationModal 
          recommendation={expandedModal} 
          onClose={() => setExpandedModal(null)} 
        />
      )}
    </div>
  );
}

// Recommendation Card Component
function RecommendationCard({ recommendation, onExpand }) {
  const [showWhy, setShowWhy] = useState(false);

  const getCategoryColor = (category) => {
    const colors = {
      scheduling: 'bg-green-100 text-green-800 border-green-300',
      compute: 'bg-blue-100 text-blue-800 border-blue-300',
      storage: 'bg-purple-100 text-purple-800 border-purple-300',
      database: 'bg-orange-100 text-orange-800 border-orange-300',
      region: 'bg-red-100 text-red-800 border-red-300',
      cost: 'bg-yellow-100 text-yellow-800 border-yellow-300'
    };
    return colors[category?.toLowerCase()] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getConfidenceColor = (confidence) => {
    const colors = {
      High: 'bg-green-100 text-green-800 border-green-300',
      Medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      Low: 'bg-orange-100 text-orange-800 border-orange-300'
    };
    return colors[confidence] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getCardStyle = (status) => {
    if (status === 'rejected') {
      return 'from-red-50/20 to-white border-red-300 hover:border-red-400';
    }
    if (status === 'flagged') {
      return 'from-yellow-50/20 to-white border-yellow-300 hover:border-yellow-400';
    }
    return 'from-gray-50 to-white border-gray-200 hover:border-green-300';
  };

  return (
    <div className={`bg-gradient-to-r ${getCardStyle(recommendation.constraint_status)} rounded-lg p-6 border-2 transition cursor-pointer`}
         onClick={onExpand}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center flex-wrap gap-2 mb-3">
            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getCategoryColor(recommendation.category)}`}>
              {recommendation.category?.toUpperCase()}
            </span>
            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getConfidenceColor(recommendation.confidence)}`}>
              {recommendation.confidence} Confidence
            </span>
            {recommendation.effort && (
              <span className="px-3 py-1 bg-gray-100 text-gray-700 border border-gray-300 rounded-full text-xs font-bold">
                Effort: {recommendation.effort}
              </span>
            )}
            {recommendation.constraint_status === 'flagged' && (
              <span className="px-3 py-1 bg-yellow-100 text-yellow-800 border border-yellow-300 rounded-full text-xs font-bold flex items-center gap-1">
                ⚠️ constraint flagged
              </span>
            )}
            {recommendation.constraint_status === 'rejected' && (
              <span className="px-3 py-1 bg-red-100 text-red-800 border border-red-300 rounded-full text-xs font-bold flex items-center gap-1">
                ❌ constraint rejected
              </span>
            )}
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-4">{recommendation.title || recommendation.recommendation}</h3>
          
          {recommendation.constraint_reason && recommendation.constraint_status !== 'compatible' && (
            <div className={`p-3 rounded text-sm mb-3 border ${
              recommendation.constraint_status === 'rejected' 
                ? 'bg-red-50 text-red-800 border-red-200' 
                : 'bg-yellow-50 text-yellow-800 border-yellow-200'
            }`}>
              {recommendation.constraint_reason}
            </div>
          )}

            <div className="bg-emerald-50 border-l-4 border-emerald-500 rounded p-3 mb-3">
              <p className="text-sm font-semibold text-emerald-950 mb-1">📈 Impact Metrics</p>
              <p className="text-sm text-emerald-900 font-bold">{recommendation.impact}</p>
              <p className="text-xs text-emerald-800 mt-1">Total potential reduction: {recommendation.carbon_reduction_kg?.toFixed(2)} kg CO₂</p>
            </div>
          )}

          {(recommendation.explanation?.why || recommendation.reasoning) && (
            <div className="bg-blue-50 border-l-4 border-blue-500 rounded p-3 mb-3">
              <p className="text-sm font-semibold text-blue-950 mb-1">💡 Why (Sustainability Mechanism)</p>
              <p className="text-sm text-blue-900">{recommendation.explanation?.why || recommendation.reasoning}</p>
            </div>
          )}
          
          {/* 3. HOW (ACTION STEPS) BLOCK */}
          {recommendation.explanation?.how && recommendation.explanation.how.length > 0 && (
            <div className="bg-indigo-50 border-l-4 border-indigo-500 rounded p-3 mb-3">
              <p className="text-sm font-semibold text-indigo-950 mb-2">🛠️ How to Implement (Action Steps)</p>
              <ul className="text-sm text-indigo-900 space-y-1 pl-1 list-none">
                {recommendation.explanation.how.map((step, sIdx) => (
                  <li key={sIdx} className="pl-1">{step}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
        
        {/* Expected Impact Badge */}
        <div className="text-right ml-6">
          <div className="bg-green-100 rounded-lg p-4 border-2 border-green-300">
            <div className="text-sm text-green-700 mb-1">Expected Impact</div>
            <div className="text-3xl font-bold text-green-900">
              {recommendation.expected_reduction_pct?.toFixed(1) || recommendation.potential_reduction_pct?.toFixed(1)}%
            </div>
            <div className="text-xs text-green-600 mt-1">
              {recommendation.expected_reduction_kg?.toFixed(2) || recommendation.potential_savings_kg?.toFixed(2)} kg CO₂
            </div>
          </div>
        </div>
      </div>

      {/* Expandable "Why this recommendation" section */}
      <div className="mt-4 pt-3 border-t border-gray-200" onClick={(e) => e.stopPropagation()}>
        <button
          onClick={() => setShowWhy(!showWhy)}
          className="flex items-center gap-2 text-sm font-semibold text-green-600 hover:text-green-700 transition"
        >
          <span>{showWhy ? 'Hide' : 'Show'} "Evidence Grid Details"</span>
          <ChevronRight className={`w-4 h-4 transform transition-transform ${showWhy ? 'rotate-90' : ''}`} />
        </button>

        {showWhy && (
          <div className="mt-3 bg-green-50/30 rounded-lg p-4 border border-green-100/60 space-y-3 text-left">
            {recommendation.root_cause && (
              <div>
                <span className="text-xs font-bold text-green-800 uppercase tracking-wider">Root Cause:</span>
                <p className="text-sm text-gray-700 mt-1">{recommendation.root_cause}</p>
              </div>
            )}

            {recommendation.evidence && typeof recommendation.evidence === 'object' && Object.keys(recommendation.evidence).length > 0 && (
              <div className="space-y-3">
                <span className="text-xs font-bold text-green-800 uppercase tracking-wider block">Structured Evidence:</span>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {recommendation.evidence.current_region && (
                    <div className="bg-white p-3 rounded border border-green-100/40">
                      <span className="text-xs text-gray-500 font-semibold uppercase block border-b pb-1 mb-1">Current State</span>
                      <div className="text-sm text-gray-700 space-y-1">
                        <div><strong className="text-xs text-gray-500 font-semibold">Zone:</strong> {recommendation.evidence.current_region.zone || 'N/A'}</div>
                        <div><strong className="text-xs text-gray-500 font-semibold">Grid Intensity:</strong> {recommendation.evidence.current_region.avg_intensity_gco2 ? `${recommendation.evidence.current_region.avg_intensity_gco2} gCO₂/kWh` : 'N/A'}</div>
                        <div><strong className="text-xs text-gray-500 font-semibold">Estimated Cost:</strong> {recommendation.evidence.current_region.monthly_cost !== undefined ? `$${recommendation.evidence.current_region.monthly_cost.toFixed(2)}` : 'N/A'}</div>
                      </div>
                    </div>
                  )}

                  {recommendation.evidence.target_region && (
                    <div className="bg-white p-3 rounded border border-green-100/40">
                      <span className="text-xs text-gray-500 font-semibold uppercase block border-b pb-1 mb-1">Target State</span>
                      <div className="text-sm text-gray-700 space-y-1">
                        <div><strong className="text-xs text-gray-500 font-semibold">Zone:</strong> {recommendation.evidence.target_region.zone || 'N/A'}</div>
                        <div><strong className="text-xs text-gray-500 font-semibold">Grid Intensity:</strong> {recommendation.evidence.target_region.avg_intensity_gco2 ? `${recommendation.evidence.target_region.avg_intensity_gco2} gCO₂/kWh` : 'N/A'}</div>
                        <div><strong className="text-xs text-gray-500 font-semibold">Estimated Cost:</strong> {recommendation.evidence.target_region.monthly_cost !== undefined ? `$${recommendation.evidence.target_region.monthly_cost.toFixed(2)}` : 'N/A'}</div>
                      </div>
                    </div>
                  )}
                </div>

                {recommendation.evidence.basis && (
                  <div className="bg-white p-3 rounded border border-green-100/40 text-sm">
                    <strong className="text-xs text-gray-500 font-semibold uppercase block mb-1">Methodology Basis:</strong>
                    <span className="text-gray-700">{recommendation.evidence.basis}</span>
                  </div>
                )}

                {recommendation.evidence.workload_pattern && (
                  <div className="bg-white p-3 rounded border border-green-100/40 text-sm">
                    <strong className="text-xs text-gray-500 font-semibold uppercase block mb-1">Workload Pattern:</strong>
                    <span className="text-gray-700">{recommendation.evidence.workload_pattern}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
      
      <div className="flex items-center justify-between pt-3 mt-4 border-t border-gray-200">
        <div className="text-sm text-gray-600">
          {recommendation.service && <span>Service: {recommendation.service}</span>}
        </div>
        <button className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-semibold text-sm">
          View Details
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

// Recommendation Detail Modal
function RecommendationModal({ recommendation, onClose }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-6"
         onClick={onClose}>
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
           onClick={(e) => e.stopPropagation()}>
        <div className={`sticky top-0 bg-gradient-to-r ${
          recommendation.constraint_status === 'rejected'
            ? 'from-red-600 to-red-800'
            : recommendation.constraint_status === 'flagged'
            ? 'from-yellow-600 to-yellow-800'
            : 'from-green-600 to-blue-600'
        } text-white p-6 rounded-t-xl`}>
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">{recommendation.title || recommendation.recommendation}</h2>
              <div className="flex items-center flex-wrap gap-2">
                <span className="px-3 py-1 bg-white/20 rounded-full text-xs font-bold">
                  {recommendation.category?.toUpperCase()}
                </span>
                <span className="px-3 py-1 bg-white/20 rounded-full text-xs font-bold">
                  {recommendation.confidence} Confidence
                </span>
                {recommendation.effort && (
                  <span className="px-3 py-1 bg-white/20 rounded-full text-xs font-bold">
                    Effort: {recommendation.effort}
                  </span>
                )}
              </div>
            </div>
            <button onClick={onClose} className="text-white hover:text-gray-200 text-2xl font-bold">
              ×
            </button>
          </div>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Constraint Warning/Error Alert */}
          {recommendation.constraint_status === 'rejected' && (
            <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-5">
              <h3 className="text-lg font-bold text-red-900 mb-2">❌ Constraint Violation</h3>
              <p className="text-red-800">{recommendation.constraint_reason}</p>
            </div>
          )}
          {recommendation.constraint_status === 'flagged' && (
            <div className="bg-yellow-50 border-l-4 border-yellow-500 rounded-lg p-5">
              <h3 className="text-lg font-bold text-yellow-900 mb-2">⚠️ Constraint Warning</h3>
              <p className="text-yellow-800">{recommendation.constraint_reason}</p>
            </div>
          )}

          {/* Impact Metrics */}
          {recommendation.impact && (
            <div className="bg-emerald-50 border-l-4 border-emerald-500 rounded-lg p-5">
              <h3 className="text-lg font-bold text-emerald-950 mb-2">📈 Impact Metrics</h3>
              <p className="text-sm text-emerald-900 font-bold">{recommendation.impact}</p>
              <p className="text-xs text-emerald-800 mt-1">Total potential reduction: {recommendation.carbon_reduction_kg?.toFixed(2)} kg CO₂</p>
            </div>
          )}

          {/* Why (Reasoning) */}
          {(recommendation.explanation?.why || recommendation.reasoning) && (
            <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-5">
              <h3 className="text-lg font-bold text-blue-900 mb-2">💡 Why (Sustainability Mechanism)</h3>
              <p className="text-blue-800">{recommendation.explanation?.why || recommendation.reasoning}</p>
            </div>
          )}
          
          {/* How (Action Steps) */}
          {recommendation.explanation?.how && recommendation.explanation.how.length > 0 && (
            <div className="bg-indigo-50 border-l-4 border-indigo-500 rounded-lg p-5">
              <h3 className="text-lg font-bold text-indigo-950 mb-2">🛠️ How to Implement (Action Steps)</h3>
              <ul className="text-sm text-indigo-900 space-y-2 list-none">
                {recommendation.explanation.how.map((step, sIdx) => (
                  <li key={sIdx}>{step}</li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Expected Impact */}
          <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-5 border-2 border-green-200">
            <h3 className="text-lg font-bold text-gray-900 mb-4">📈 Expected Impact</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white rounded-lg p-4 border border-green-200">
                <div className="text-sm text-gray-600 mb-1">Carbon Reduction</div>
                <div className="text-2xl font-bold text-green-900">
                  {recommendation.expected_reduction_kg?.toFixed(2) || recommendation.potential_savings_kg?.toFixed(2)} kg
                </div>
                <div className="text-xs text-green-600 mt-1">
                  {recommendation.expected_reduction_pct?.toFixed(1) || recommendation.potential_reduction_pct?.toFixed(1)}%
                </div>
              </div>
              <div className="bg-white rounded-lg p-4 border border-blue-200">
                <div className="text-sm text-gray-600 mb-1">Cost Impact</div>
                <div className="text-xl font-bold text-blue-900">{recommendation.cost_impact || 'Neutral'}</div>
              </div>
              <div className="bg-white rounded-lg p-4 border border-purple-200">
                <div className="text-sm text-gray-600 mb-1">Confidence</div>
                <div className="text-xl font-bold text-purple-900">{recommendation.confidence}</div>
              </div>
            </div>
          </div>
          
          {/* Implementation Notes */}
          {recommendation.implementation_notes && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-5">
              <h3 className="text-lg font-bold text-gray-900 mb-2">🛠️ Implementation Notes</h3>
              <p className="text-gray-700 whitespace-pre-line">{recommendation.implementation_notes}</p>
            </div>
          )}
          
          {/* Constraint Validation Results */}
          {recommendation.constraints_applied && recommendation.constraints_applied.length > 0 && (
            <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-5">
              <h3 className="text-lg font-bold text-indigo-900 mb-3">✅ Constraint Validation</h3>
              <div className="flex flex-wrap gap-2">
                {recommendation.constraints_applied.map((constraint, i) => (
                  <span key={i} className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-semibold">
                    {constraint}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {/* Affected Services/Regions */}
          <div className="grid grid-cols-2 gap-4">
            {recommendation.service && (
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-blue-900 mb-2">Affected Service</h4>
                <p className="text-blue-800">{recommendation.service}</p>
              </div>
            )}
            {recommendation.region && (
              <div className="bg-green-50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-green-900 mb-2">Affected Region</h4>
                <p className="text-green-800">{recommendation.region}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
