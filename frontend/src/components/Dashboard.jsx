import { useState } from 'react';
import MetricsBar from './MetricsBar';
import EmissionsPieChart from './EmissionsPieChart';
import TrendChart from './TrendChart';
import DataTable from './DataTable';
import AIInsightsPanel from './AIInsightsPanel';
import WhatIfSimulator from './WhatIfSimulator';
import UploadSection from './UploadSection';
import CloudSimulationPanel from './CloudSimulationPanel';

function Dashboard({ awsData, insights, loading, onUpload, onLoadMock }) {
  const [activeTab, setActiveTab] = useState('overview');

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">CarbonIQ Cloud Analyzer</h1>
              <p className="text-slate-400 text-sm">AWS Billing → Carbon Intelligence</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setActiveTab('simulation')}
                className={`px-4 py-2 rounded-lg transition ${
                  activeTab === 'simulation'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                Simulation & Custom Data
              </button>
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-4 py-2 rounded-lg transition ${
                  activeTab === 'overview'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                AWS Overview
              </button>
              <button
                onClick={() => setActiveTab('insights')}
                className={`px-4 py-2 rounded-lg transition ${
                  activeTab === 'insights'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                AI Insights
              </button>
              <button
                onClick={() => setActiveTab('whatif')}
                className={`px-4 py-2 rounded-lg transition ${
                  activeTab === 'whatif'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                What-If
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        
        {activeTab === 'simulation' && (
          <CloudSimulationPanel />
        )}

        {activeTab !== 'simulation' && (
          <UploadSection onUpload={onUpload} onLoadMock={onLoadMock} />
        )}

        {awsData && activeTab !== 'simulation' && (
          <>
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <MetricsBar data={awsData} />
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <EmissionsPieChart data={awsData.by_service} title="Emissions by Service" />
                  <TrendChart data={awsData.by_region} title="Emissions by Region" />
                </div>

                {awsData.by_instance && awsData.by_instance.length > 0 && (
                  <TrendChart data={awsData.by_instance} title="Emissions by Instance Type" dataKey="instance" />
                )}

                {awsData.idle_resources && awsData.idle_resources.length > 0 && (
                  <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-yellow-500/30">
                    <h3 className="text-lg font-semibold text-yellow-400 mb-4">⚠️ Idle Resources Detected</h3>
                    <div className="space-y-2">
                      {awsData.idle_resources.map((resource, idx) => (
                        <div key={idx} className="bg-slate-700/50 p-3 rounded-lg text-sm">
                          <span className="text-white font-medium">{resource.service}</span>
                          <span className="text-slate-400"> in {resource.region}</span>
                          {resource.instance_type && (
                            <span className="text-slate-400"> ({resource.instance_type})</span>
                          )}
                          <span className="text-yellow-400 ml-4">
                            Low usage: {resource.usage} | Cost: ${resource.cost}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <DataTable data={awsData.line_items} />
              </div>
            )}

            {activeTab === 'insights' && insights && (
              <AIInsightsPanel insights={insights} />
            )}

            {activeTab === 'whatif' && (
              <WhatIfSimulator awsData={awsData} />
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default Dashboard;
