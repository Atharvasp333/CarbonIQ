export default function ScopeAnalysis({ emissionData }) {
  if (!emissionData) return null;

  const total = emissionData.total_co2_kg;
  const scope1 = total * 0.08;
  const scope2 = total * 0.62;
  const scope3 = total * 0.30;

  const itSectorAvg = 268;
  const bestInClass = 120;

  const roadmap = [
    { quarter: 'Q3 2026', title: 'LED Migration', status: 'In Progress', target: '15% reduction' },
    { quarter: 'Q4 2026', title: 'Server Optimization', status: 'Planned', target: '20% reduction' },
    { quarter: 'Q1 2027', title: 'Solar Installation', status: 'Planned', target: '30% reduction' }
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold mb-4">GHG Protocol Scope Breakdown</h3>
        
        <div className="space-y-4">
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Scope 1 (Direct)</span>
              <span className="text-sm text-gray-600">{scope1.toFixed(2)} kg (8%)</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div className="bg-red-500 h-4 rounded-l-full" style={{ width: '8%' }}></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Scope 2 (Electricity)</span>
              <span className="text-sm text-gray-600">{scope2.toFixed(2)} kg (62%)</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div className="bg-amber-500 h-4" style={{ width: '62%', marginLeft: '8%' }}></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Scope 3 (Indirect)</span>
              <span className="text-sm text-gray-600">{scope3.toFixed(2)} kg (30%)</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div className="bg-green-500 h-4 rounded-r-full" style={{ width: '30%', marginLeft: '70%' }}></div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold mb-4">Industry Benchmark</h3>
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="w-32 text-sm font-medium">Your Company</div>
            <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
              <div 
                className="bg-blue-600 h-6 rounded-full flex items-center justify-end pr-2"
                style={{ width: `${(total / itSectorAvg * 100).toFixed(0)}%` }}
              >
                <span className="text-xs text-white font-semibold">{total.toFixed(0)} kg</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="w-32 text-sm font-medium">IT Sector Avg</div>
            <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
              <div className="bg-gray-500 h-6 rounded-full flex items-center justify-end pr-2" style={{ width: '100%' }}>
                <span className="text-xs text-white font-semibold">{itSectorAvg} kg</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="w-32 text-sm font-medium">Best-in-Class</div>
            <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
              <div 
                className="bg-green-600 h-6 rounded-full flex items-center justify-end pr-2"
                style={{ width: `${(bestInClass / itSectorAvg * 100).toFixed(0)}%` }}
              >
                <span className="text-xs text-white font-semibold">{bestInClass} kg</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold mb-4">Decarbonization Roadmap</h3>
        <div className="space-y-3">
          {roadmap.map((item, idx) => (
            <div key={idx} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <div className="font-semibold">{item.quarter}</div>
                  <div className="text-sm text-gray-600">{item.title}</div>
                </div>
                <span className={`text-xs px-2 py-1 rounded ${
                  item.status === 'In Progress' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {item.status}
                </span>
              </div>
              <div className="text-sm font-medium text-primary">{item.target}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
