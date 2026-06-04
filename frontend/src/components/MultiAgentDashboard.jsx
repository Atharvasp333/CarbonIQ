import React, { useState } from 'react';
import { Upload, Activity, TrendingDown, AlertCircle, Zap, MapPin } from 'lucide-react';
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000 // 30 second timeout (reduced for debug mode - only 1000 rows)
});

const MultiAgentDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState('');
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [serviceDetail, setServiceDetail] = useState(null);
  const [loadingService, setLoadingService] = useState(false);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    console.log('[Upload] Starting file upload:', file.name);
    setLoading(true);
    setError(null);
    setResults(null); // Clear previous results
    setProgress('Uploading CSV (processing first 1000 rows only)...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      console.log('[Upload] Sending POST request to /api/multi-agent/analyze');
      setProgress('Processing through multi-agent pipeline (1000 rows)...');
      const startTime = Date.now();
      
      const response = await apiClient.post('/api/multi-agent/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const elapsed = Date.now() - startTime;
      console.log(`[Upload] Response received in ${elapsed}ms`);
      console.log('[Upload] Response data:',  response.data);

      // Check if response has success field
      if (response.data && response.data.success === false) {
        throw new Error(response.data.message || 'Analysis failed');
      }

      setProgress('Generating dashboard...');
      
      // Even if partial data, display it
      if (response.data && response.data.summary) {
        setResults(response.data);
        console.log('[Upload] Dashboard data set');
      } else {
        throw new Error('Invalid response format from server');
      }
      
      // Store results for service drill-down (non-blocking)
      try {
        console.log('[Upload] Storing results for service analytics');
        await apiClient.post('/api/service-analytics/store', response.data);
        console.log('[Upload] Service analytics stored');
      } catch (storeErr) {
        console.warn('[Upload] Failed to store service analytics:', storeErr);
        // Don't fail the whole operation if storage fails
      }
      
      console.log('[Upload] Complete');
      setProgress('');
    } catch (err) {
      console.error('[Upload] Error:', err);
      console.error('[Upload] Error response:', err.response?.data);
      
      // If we got a response with data, check if it has a message
      const errorMsg = err.response?.data?.message || 
                      err.response?.data?.detail || 
                      err.message || 
                      'Analysis failed - please try again';
      
      setError(errorMsg);
      setProgress('');
    } finally {
      setLoading(false);
    }
  };

  const loadDemoData = async () => {
    console.log('[Demo] Starting demo data load');
    setLoading(true);
    setError(null);
    setResults(null); // Clear previous results
    setProgress('Loading demo CUR data (first 1000 rows)...');

    try {
      console.log('[Demo] Sending POST request to /api/multi-agent/analyze-demo');
      setProgress('Processing demo data through pipeline (1000 rows)...');
      const startTime = Date.now();
      
      const response = await apiClient.post('/api/multi-agent/analyze-demo', {
        load_demo: true
      });

      const elapsed = Date.now() - startTime;
      console.log(`[Demo] Response received in ${elapsed}ms`);
      console.log('[Demo] Response data:', response.data);

      // Check if response has success field
      if (response.data && response.data.success === false) {
        throw new Error(response.data.message || 'Demo load failed');
      }

      setProgress('Generating dashboard...');
      
      // Even if partial data, display it
      if (response.data && response.data.summary) {
        setResults(response.data);
        console.log('[Demo] Dashboard data set');
      } else {
        throw new Error('Invalid response format from server');
      }
      
      // Store results for service drill-down (non-blocking)
      try {
        console.log('[Demo] Storing results for service analytics');
        await apiClient.post('/api/service-analytics/store', response.data);
        console.log('[Demo] Service analytics stored');
      } catch (storeErr) {
        console.warn('[Demo] Failed to store service analytics:', storeErr);
        // Don't fail the whole operation if storage fails
      }
      
      console.log('[Demo] Complete');
      setProgress('');
    } catch (err) {
      console.error('[Demo] Error:', err);
      console.error('[Demo] Error response:', err.response?.data);
      
      const errorMsg = err.response?.data?.message || 
                      err.response?.data?.detail || 
                      err.message || 
                      'Demo load failed - please try again';
      setError(errorMsg);
      setProgress('');
    } finally {
      setLoading(false);
    }
  };

  const handleServiceClick = async (serviceName) => {
    setLoadingService(true);
    try {
      const response = await apiClient.get(`/api/service-analytics/${serviceName}`);
      setServiceDetail(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load service details');
    } finally {
      setLoadingService(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-4">
            Multi-Agent Carbon Intelligence
          </h1>
          <p className="text-xl text-blue-300">
            AI-Powered AWS CUR Analysis with 6 Specialized Agents
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 mb-8 border border-white/20">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-center">
            <label className="flex-1 max-w-md">
              <div className="flex items-center justify-center gap-3 px-6 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl cursor-pointer transition-all duration-200 transform hover:scale-105">
                <Upload size={24} />
                <span className="font-semibold">Upload AWS CUR CSV</span>
              </div>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                className="hidden"
                disabled={loading}
              />
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
              <p className="text-gray-400 text-sm mt-2">
                Processing first 1,000 rows for fast response (30 seconds max)
              </p>
              <p className="text-gray-500 text-xs mt-1">
                Optimizations: Column filtering → Row compression → API deduplication
              </p>
            </div>
          )}

          {error && (
            <div className="mt-6 p-4 bg-red-500/20 border border-red-500 rounded-lg">
              <p className="text-red-200 font-semibold mb-2">Error</p>
              <p className="text-red-100">{error}</p>
              {error.includes('API key') && (
                <p className="text-red-100 mt-2 text-sm">
                  💡 Set the ELECTRICITY_MAPS_API_KEY environment variable to enable carbon intensity data.
                </p>
              )}
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
                value={`${results.summary.total_emissions_kg.toFixed(2)} kg`}
                subtitle={`CO₂ from ${results.pipeline_stats.ingestion.original_rows || results.pipeline_stats.ingestion.processed_rows} rows`}
                icon={<Activity className="text-red-400" size={32} />}
                bgColor="bg-red-500/20"
              />
              <SummaryCard
                title="Total Cost"
                value={`$${results.summary.total_cost.toFixed(2)}`}
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

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              
              {/* Emissions by Service */}
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                <h3 className="text-2xl font-bold text-white mb-4">Emissions by Service</h3>
                <div className="space-y-3">
                  {results.analytics.service_breakdown.slice(0, 5).map((service, idx) => (
                    <div 
                      key={idx} 
                      className="bg-white/5 rounded-lg p-4 cursor-pointer hover:bg-white/10 transition-all transform hover:scale-102"
                      onClick={() => handleServiceClick(service.service.toLowerCase())}
                    >
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-white font-semibold flex items-center gap-2">
                          {service.service}
                          <span className="text-xs text-gray-400">→ Click for details</span>
                        </span>
                        <span className="text-green-300">{service.emissions_kg.toFixed(2)} kg</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-red-500 to-orange-500 h-2 rounded-full"
                          style={{
                            width: `${(service.emissions_kg / results.summary.total_emissions_kg) * 100}%`
                          }}
                        ></div>
                      </div>
                      <div className="flex justify-between text-sm text-gray-400 mt-1">
                        <span>Cost: ${service.cost.toFixed(2)}</span>
                        <span>Energy: {service.energy_kwh.toFixed(2)} kWh</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Emissions by Region */}
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                <h3 className="text-2xl font-bold text-white mb-4">Emissions by Region</h3>
                <div className="space-y-3">
                  {results.analytics.region_breakdown.slice(0, 5).map((region, idx) => (
                    <div key={idx} className="bg-white/5 rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-white font-semibold">{region.region}</span>
                        <span className="text-blue-300">{region.emissions_kg.toFixed(2)} kg</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                          style={{
                            width: `${(region.emissions_kg / results.summary.total_emissions_kg) * 100}%`
                          }}
                        ></div>
                      </div>
                      <div className="flex justify-between text-sm text-gray-400 mt-1">
                        <span>Zone: {region.zone}</span>
                        <span>Intensity: {region.avg_carbon_intensity} gCO₂/kWh</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Optimization Insights */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 mb-8">
              <h3 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <TrendingDown className="text-green-400" />
                Optimization Opportunities
              </h3>
              
              <div className="bg-green-500/20 border border-green-500 rounded-lg p-4 mb-6">
                <h4 className="text-xl font-bold text-green-300 mb-2">Potential Savings</h4>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-3xl font-bold text-white">
                      {results.optimization.reduction_estimates.total_potential_reduction_kg.toFixed(1)} kg
                    </div>
                    <div className="text-green-300">CO₂ Reduction</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-white">
                      ${results.optimization.reduction_estimates.total_potential_cost_savings.toFixed(2)}
                    </div>
                    <div className="text-green-300">Cost Savings</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-white">
                      {results.optimization.reduction_estimates.percentage_reduction.toFixed(1)}%
                    </div>
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
                          <span className="font-semibold text-white capitalize">{opp.type.replace('_', ' ')}</span>
                          <span className={`px-2 py-1 rounded text-xs font-bold ${
                            opp.priority === 'high' ? 'bg-red-500' : 'bg-yellow-500'
                          } text-white`}>
                            {opp.priority.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-gray-300 text-sm">{opp.description}</p>
                        {opp.reduction_kg && (
                          <div className="mt-2 text-green-400 text-sm font-semibold">
                            💡 Save {opp.reduction_kg.toFixed(1)} kg CO₂
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Detailed Table */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
              <h3 className="text-2xl font-bold text-white mb-4">Detailed Workload Analysis</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-white/20">
                      <th className="pb-3 text-gray-300 font-semibold">Service</th>
                      <th className="pb-3 text-gray-300 font-semibold">Region</th>
                      <th className="pb-3 text-gray-300 font-semibold">Usage</th>
                      <th className="pb-3 text-gray-300 font-semibold">Cost</th>
                      <th className="pb-3 text-gray-300 font-semibold">Carbon Intensity</th>
                      <th className="pb-3 text-gray-300 font-semibold">Emissions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.detailed_records.slice(0, 20).map((record, idx) => (
                      <tr key={idx} className="border-b border-white/10">
                        <td className="py-3 text-white">{record.service}</td>
                        <td className="py-3 text-gray-300">{record.region}</td>
                        <td className="py-3 text-gray-300">{record.usage_amount.toFixed(2)}</td>
                        <td className="py-3 text-green-300">${record.cost.toFixed(2)}</td>
                        <td className="py-3 text-yellow-300">{record.carbon_intensity} g/kWh</td>
                        <td className="py-3 text-red-300">{record.emissions_kg.toFixed(4)} kg</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Pipeline Stats */}
            <div className="mt-8 bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10">
              <h4 className="text-lg font-bold text-gray-400 mb-4">Pipeline Performance Statistics</h4>
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-center">
                <StatBadge 
                  label="Original Rows" 
                  value={results.pipeline_stats.ingestion.original_rows || results.pipeline_stats.ingestion.processed_rows} 
                />
                <StatBadge 
                  label="Compressed To" 
                  value={results.pipeline_stats.ingestion.compressed_rows} 
                />
                <StatBadge 
                  label="Compression" 
                  value={results.pipeline_stats.ingestion.compression_ratio || '0%'} 
                />
                <StatBadge label="API Calls" value={results.pipeline_stats.carbon_intensity.api_calls} />
                <StatBadge label="Cache Hits" value={results.pipeline_stats.carbon_intensity.cached_calls} />
                <StatBadge label="Opportunities" value={results.optimization.opportunities.length} />
              </div>
              {results.pipeline_stats.carbon_intensity.failed_calls > 0 && (
                <div className="mt-4 p-3 bg-yellow-500/20 border border-yellow-500 rounded-lg">
                  <p className="text-yellow-200 text-sm">
                    ⚠ {results.pipeline_stats.carbon_intensity.failed_calls} API calls failed.
                    {!results.pipeline_stats.carbon_intensity.has_api_key && 
                      ' No API key configured - set ELECTRICITY_MAPS_API_KEY environment variable.'}
                  </p>
                </div>
              )}
            </div>

            {/* Service Detail Modal */}
            {serviceDetail && (
              <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto" onClick={() => setServiceDetail(null)}>
                <div className="bg-gradient-to-br from-gray-900 to-blue-900 rounded-2xl border border-white/20 max-w-6xl w-full my-8" onClick={(e) => e.stopPropagation()}>
                  <div className="p-6">
                    <div className="flex justify-between items-center mb-6">
                      <h2 className="text-3xl font-bold text-white">{serviceDetail.service_name} Detailed Analytics</h2>
                      <button 
                        onClick={() => setServiceDetail(null)}
                        className="text-gray-400 hover:text-white text-2xl font-bold w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/10"
                      >
                        ✕
                      </button>
                    </div>

                    {/* Summary Cards */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                      <div className="bg-red-500/20 rounded-lg p-4 border border-red-500/30">
                        <div className="text-red-300 text-sm mb-1">Total Emissions</div>
                        <div className="text-2xl font-bold text-white">{serviceDetail.summary?.total_emissions_kg?.toFixed(2) || 0} kg</div>
                      </div>
                      <div className="bg-green-500/20 rounded-lg p-4 border border-green-500/30">
                        <div className="text-green-300 text-sm mb-1">Total Cost</div>
                        <div className="text-2xl font-bold text-white">${serviceDetail.summary?.total_cost?.toFixed(2) || 0}</div>
                      </div>
                      <div className="bg-blue-500/20 rounded-lg p-4 border border-blue-500/30">
                        <div className="text-blue-300 text-sm mb-1">Executions</div>
                        <div className="text-2xl font-bold text-white">{serviceDetail.summary?.number_of_executions || 0}</div>
                      </div>
                      <div className="bg-yellow-500/20 rounded-lg p-4 border border-yellow-500/30">
                        <div className="text-yellow-300 text-sm mb-1">Avg Carbon Intensity</div>
                        <div className="text-2xl font-bold text-white">{serviceDetail.summary?.average_carbon_intensity?.toFixed(0) || 0} g/kWh</div>
                      </div>
                    </div>

                    {/* Two Column Layout */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                      
                      {/* Region Breakdown */}
                      {serviceDetail.region_breakdown && serviceDetail.region_breakdown.length > 0 && (
                        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                          <h3 className="text-xl font-bold text-white mb-3">Region Breakdown</h3>
                          <div className="space-y-2 max-h-64 overflow-y-auto">
                            {serviceDetail.region_breakdown.slice(0, 5).map((region, idx) => (
                              <div key={idx} className="bg-white/5 rounded-lg p-3">
                                <div className="flex justify-between items-center mb-1">
                                  <span className="text-white font-semibold">{region.region}</span>
                                  <span className="text-red-300">{region.emissions_kg?.toFixed(2) || 0} kg</span>
                                </div>
                                <div className="text-sm text-gray-400">
                                  Runs: {region.runs} | Cost: ${region.cost?.toFixed(2) || 0} | Intensity: {region.avg_carbon_intensity?.toFixed(0) || 0} g/kWh
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Peak Events */}
                      {serviceDetail.peak_emission_events && serviceDetail.peak_emission_events.length > 0 && (
                        <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                          <h3 className="text-xl font-bold text-white mb-3">Top Emission Events</h3>
                          <div className="space-y-2 max-h-64 overflow-y-auto">
                            {serviceDetail.peak_emission_events.slice(0, 5).map((event, idx) => (
                              <div key={idx} className="bg-orange-500/10 border-l-4 border-orange-500 rounded-lg p-3">
                                <div className="flex justify-between items-center mb-1">
                                  <span className="text-white font-semibold">{event.region}</span>
                                  <span className="text-orange-300">{event.emissions_kg?.toFixed(4) || 0} kg</span>
                                </div>
                                <div className="text-xs text-gray-400">
                                  {event.time?.split('T')[0] || 'N/A'} | Intensity: {event.carbon_intensity} g/kWh
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Optimization Recommendations */}
                    {serviceDetail.optimization_insights && serviceDetail.optimization_insights.recommendations && serviceDetail.optimization_insights.recommendations.length > 0 && (
                      <div className="bg-green-500/10 rounded-xl p-4 border border-green-500/30 mb-6">
                        <h3 className="text-xl font-bold text-green-300 mb-3">💡 Optimization Recommendations</h3>
                        
                        {serviceDetail.optimization_insights.estimated_savings && (
                          <div className="grid grid-cols-3 gap-4 mb-4 p-3 bg-green-500/20 rounded-lg">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-white">
                                {serviceDetail.optimization_insights.estimated_savings.emissions_reduction_kg?.toFixed(1) || 0} kg
                              </div>
                              <div className="text-sm text-green-200">Potential Reduction</div>
                            </div>
                            <div className="text-center">
                              <div className="text-2xl font-bold text-white">
                                ${serviceDetail.optimization_insights.estimated_savings.cost_reduction?.toFixed(2) || 0}
                              </div>
                              <div className="text-sm text-green-200">Cost Savings</div>
                            </div>
                            <div className="text-center">
                              <div className="text-2xl font-bold text-white">
                                {serviceDetail.optimization_insights.estimated_savings.efficiency_gain_percentage || 0}%
                              </div>
                              <div className="text-sm text-green-200">Efficiency Gain</div>
                            </div>
                          </div>
                        )}
                        
                        <div className="space-y-2">
                          {serviceDetail.optimization_insights.recommendations.map((rec, idx) => (
                            <div key={idx} className="bg-white/5 rounded-lg p-3 text-white text-sm">
                              • {rec}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* What-If Scenarios */}
                    {serviceDetail.whatif_scenarios && serviceDetail.whatif_scenarios.length > 0 && (
                      <div className="bg-purple-500/10 rounded-xl p-4 border border-purple-500/30">
                        <h3 className="text-xl font-bold text-purple-300 mb-3">🔮 What-If Scenarios</h3>
                        <div className="space-y-3">
                          {serviceDetail.whatif_scenarios.map((scenario, idx) => (
                            <div key={idx} className="bg-white/5 rounded-lg p-4">
                              <div className="flex justify-between items-start mb-2">
                                <div>
                                  <h4 className="text-white font-semibold">{scenario.title}</h4>
                                  <div className="text-sm text-gray-400">
                                    {scenario.current} → {scenario.alternative}
                                  </div>
                                </div>
                                <div className="text-right">
                                  <div className="text-2xl font-bold text-purple-300">
                                    {scenario.potential_reduction_percentage}%
                                  </div>
                                  <div className="text-xs text-gray-400">reduction</div>
                                </div>
                              </div>
                              <div className="text-green-300 text-sm font-semibold">
                                Save: {scenario.potential_reduction_kg?.toFixed(1) || 0} kg CO₂
                                {scenario.potential_cost_savings && ` | $${scenario.potential_cost_savings.toFixed(2)}`}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {loadingService && (
              <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent"></div>
                  <p className="text-white mt-4 text-xl">Loading service details...</p>
                </div>
              </div>
            )}
          </>
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
        <h3 className="text-3xl font-bold text-white">{value}</h3>
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
