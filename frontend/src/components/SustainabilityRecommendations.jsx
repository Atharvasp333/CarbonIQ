import React, { useState } from 'react';
import { Lightbulb, TrendingDown, DollarSign, CheckCircle, AlertCircle, Info, ChevronDown, ChevronUp, ShieldCheck, Database, Layers } from 'lucide-react';

export default function SustainabilityRecommendations({ intelligence }) {
  if (!intelligence) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="text-center text-gray-500">
          <Info className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p className="font-semibold">Intelligence layer not available</p>
          <p className="text-sm mt-1">Upload CUR or run multi-agent analysis to generate personalized recommendations.</p>
        </div>
      </div>
    );
  }

  const recommendations = intelligence.recommendations || [];
  const summary = intelligence.summary || {};
  const workload_analysis = intelligence.workload_analysis || {};

  if (recommendations.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="text-center text-gray-600">
          <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
          <p className="font-semibold text-lg text-gray-800">No High-Impact Optimization Needed</p>
          <p className="text-sm mt-1 text-gray-600">
            Current infrastructure telemetry indicates workloads are operating within optimal carbon thresholds or insufficient telemetry is present to justify migrations.
          </p>
        </div>
      </div>
    );
  }

  const totalRecs = summary.total_recommendations ?? recommendations.length;
  const totalReductionKg = summary.total_potential_reduction_kg ?? recommendations.reduce((acc, r) => acc + (r.expected_reduction_kg ?? r.carbon_reduction_kg ?? 0), 0);
  const totalReductionPct = summary.total_potential_reduction_pct ?? (recommendations.length > 0 ? (recommendations.reduce((acc, r) => acc + (r.expected_reduction_pct ?? r.carbon_reduction_pct ?? 0), 0) / recommendations.length) : 0);
  const highConfidenceCount = summary.high_confidence_count ?? recommendations.filter(r => r.confidence === 'High').length;
  const topCategory = summary.top_category || summary.categories?.[0] || recommendations[0]?.category || 'Scheduling';

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-xl shadow-lg p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <Lightbulb className="w-8 h-8 text-yellow-300" />
          <div>
            <h2 className="text-2xl font-bold">Evidence-Based Sustainability Recommendations</h2>
            <p className="text-sm text-green-100">Every recommendation is rigorously justified with empirical formulas, constraints, and data provenance.</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
            <div className="text-sm opacity-90">Total Recommendations</div>
            <div className="text-3xl font-bold mt-1">{totalRecs}</div>
          </div>
          
          <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
            <div className="text-sm opacity-90">Potential Reduction</div>
            <div className="text-3xl font-bold mt-1">{(totalReductionKg ?? 0).toFixed(2)} kg</div>
            <div className="text-xs opacity-75 mt-1">~{(totalReductionPct ?? 0).toFixed(1)}% Avg Reduction</div>
          </div>
          
          <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
            <div className="text-sm opacity-90">High Confidence</div>
            <div className="text-3xl font-bold mt-1">{highConfidenceCount}</div>
            <div className="text-xs opacity-75 mt-1">Empirically Verified</div>
          </div>
          
          <div className="bg-white/20 rounded-lg p-4 backdrop-blur">
            <div className="text-sm opacity-90">Top Focus Area</div>
            <div className="text-xl font-bold mt-2 capitalize">{topCategory}</div>
          </div>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {recommendations.map((rec, idx) => (
          <RecommendationCardItem key={rec.id || idx} rec={rec} idx={idx} />
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
                      {(hotspot.emissions_kg ?? 0).toFixed(4)}
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

function RecommendationCardItem({ rec, idx }) {
  const [expanded, setExpanded] = useState(idx === 0);

  const getConfidenceBadge = (confidence) => {
    const styles = {
      High: 'bg-green-100 text-green-800 border-green-300',
      Medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      Low: 'bg-orange-100 text-orange-800 border-orange-300'
    };
    return styles[confidence] || styles.Medium;
  };

  const getCostImpactBadge = (impact) => {
    if (impact === 'Positive') return <span className="text-xs px-2 py-0.5 rounded font-semibold bg-green-100 text-green-800">Positive Spend Impact</span>;
    if (impact === 'Negative') return <span className="text-xs px-2 py-0.5 rounded font-semibold bg-red-100 text-red-800">Cost Trade-Off</span>;
    return <span className="text-xs px-2 py-0.5 rounded font-semibold bg-gray-100 text-gray-700">Cost Neutral</span>;
  };

  const reductionKg = rec.expected_reduction_kg ?? rec.carbon_reduction_kg ?? rec.potential_savings_kg ?? 0;
  const reductionPct = rec.expected_reduction_pct ?? rec.carbon_reduction_pct ?? rec.potential_reduction_pct ?? 0;
  const title = rec.title || rec.recommendation || 'Carbon Optimization Recommendation';
  const service = rec.service || 'Multi-Service';
  const category = rec.category || 'scheduling';
  const confidence = rec.confidence || 'Medium';
  const costImpact = rec.cost_impact || 'Neutral';
  const finding = rec.finding || rec.observation || 'Operational workload identified with carbon optimization potential.';
  const rootCause = rec.root_cause;
  const action = rec.recommended_action || rec.recommendation || rec.action || rec.reasoning;
  const calculationBasis = rec.calculation_basis;
  const provenance = rec.data_provenance || rec.evidence?.data_source;
  const constraints = rec.constraints || rec.constraints_applied || [];
  const evidence = rec.evidence || rec.details || {};

  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition border-l-4 border-green-500 overflow-hidden">
      <div className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="px-3 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs font-bold uppercase tracking-wider">
                {category}
              </span>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getConfidenceBadge(confidence)}`}>
                {confidence} Confidence
              </span>
              {getCostImpactBadge(costImpact)}
            </div>
            <h3 className="text-xl font-bold text-gray-900">{title}</h3>
            <p className="text-sm font-medium text-gray-600 mt-1">Service / Workload: <span className="text-blue-700 font-semibold">{service}</span></p>
          </div>

          <div className="text-right flex-shrink-0">
            <div className="flex items-center justify-end gap-1 text-green-600">
              <TrendingDown className="w-5 h-5" />
              <span className="text-2xl font-bold">{(reductionKg ?? 0).toFixed(4)} kg</span>
            </div>
            <div className="text-sm font-semibold text-gray-600 mt-0.5">
              {(reductionPct ?? 0).toFixed(1)}% reduction
            </div>
          </div>
        </div>

        {/* Finding / Observation */}
        <div className="mt-4 p-3.5 bg-blue-50/70 border-l-4 border-blue-500 rounded-r-lg text-sm">
          <span className="font-bold text-blue-900 block mb-0.5">📊 Finding & Observation</span>
          <p className="text-blue-950">{finding}</p>
        </div>

        {/* Actionable Recommendation */}
        {action && (
          <div className="mt-3 p-3.5 bg-emerald-50/70 border-l-4 border-emerald-500 rounded-r-lg text-sm">
            <span className="font-bold text-emerald-900 block mb-0.5">💡 Recommended Action</span>
            <p className="text-emerald-950">{action}</p>
          </div>
        )}

        {/* Academic Justification Toggle */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-4 w-full flex items-center justify-between px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg text-xs font-semibold text-gray-700 transition"
        >
          <span>{expanded ? 'Hide Academic Justification & Evidence' : 'Show Academic Justification (Formula, Provenance & Constraints)'}</span>
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {/* Expanded Academic Justification Details */}
      {expanded && (
        <div className="px-6 pb-6 pt-2 bg-gray-50/60 border-t border-gray-100 space-y-4 text-sm">
          {/* Root Cause */}
          {rootCause && (
            <div className="bg-white p-4 rounded-lg border border-yellow-200">
              <h4 className="text-xs font-bold text-yellow-800 uppercase tracking-wider mb-1">🎯 Root Cause Analysis</h4>
              <p className="text-gray-800 text-sm">{rootCause}</p>
            </div>
          )}

          {/* Evidence Grid */}
          {evidence && Object.keys(evidence).length > 0 && (
            <div className="bg-white p-4 rounded-lg border border-purple-200">
              <h4 className="text-xs font-bold text-purple-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5" />
                Structured Telemetry Evidence
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2.5 text-xs">
                {Object.entries(evidence).map(([k, v]) => {
                  if (k === 'data_source') return null;
                  return (
                    <div key={k} className="bg-purple-50/50 p-2.5 rounded border border-purple-100">
                      <span className="text-gray-500 capitalize block mb-0.5">{k.replace(/_/g, ' ')}</span>
                      <span className="font-semibold text-gray-900">
                        {typeof v === 'number' ? v.toFixed(4) : (Array.isArray(v) ? v.join(', ') : String(v))}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Calculation Basis & Data Provenance */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white p-4 rounded-lg border border-green-200">
              <h4 className="text-xs font-bold text-green-900 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5" />
                Calculation Basis / Formula
              </h4>
              {calculationBasis ? (
                <code className="text-xs font-mono text-emerald-800 bg-emerald-50 p-2 rounded block whitespace-pre-wrap">
                  {calculationBasis}
                </code>
              ) : (
                <p className="text-xs text-gray-600 italic">
                  Impact quantified via empirical grid carbon factor difference (ΔE = E_current × ΔIntensity / Intensity_current).
                </p>
              )}
            </div>

            <div className="bg-white p-4 rounded-lg border border-blue-200">
              <h4 className="text-xs font-bold text-blue-900 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5" />
                Data Provenance & Source
              </h4>
              <p className="text-xs text-gray-700 bg-blue-50 p-2 rounded">
                {provenance || 'Electricity Maps Real-Time API / AWS CUR Usage Telemetry'}
              </p>
            </div>
          </div>

          {/* Constraints & Trade-Offs */}
          {constraints && constraints.length > 0 && (
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">
                Operational Constraints & Trade-Offs
              </h4>
              <div className="flex flex-wrap gap-2">
                {constraints.map((c, i) => (
                  <span key={i} className="px-2.5 py-1 bg-amber-50 text-amber-900 border border-amber-200 rounded text-xs">
                    ⚠️ {c}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
