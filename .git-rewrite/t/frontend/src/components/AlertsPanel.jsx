export default function AlertsPanel({ emissionData }) {
  if (!emissionData) return null;

  const alerts = [
    {
      severity: 'red',
      title: 'Budget Threshold Warning',
      message: emissionData.total_co2_kg > 200 
        ? `Daily emissions (${emissionData.total_co2_kg.toFixed(2)} kg) exceed 200 kg threshold`
        : 'Daily emissions within acceptable range',
      active: emissionData.total_co2_kg > 200
    },
    {
      severity: 'yellow',
      title: 'Server Spike Detected',
      message: 'Server power consumption increased 12% during peak hours (2-4 PM)',
      active: true
    },
    {
      severity: 'green',
      title: 'Grid Optimization Window',
      message: 'Grid is cleaner between 7am–9am — schedule workloads now for 15% lower emissions',
      active: true
    }
  ];

  const severityStyles = {
    red: 'bg-red-50 border-red-200 text-red-800',
    yellow: 'bg-amber-50 border-amber-200 text-amber-800',
    green: 'bg-green-50 border-green-200 text-green-800'
  };

  const severityIcons = {
    red: '🚨',
    yellow: '⚠️',
    green: '✅'
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        {alerts.filter(a => a.active).map((alert, idx) => (
          <div key={idx} className={`rounded-xl border-2 p-6 ${severityStyles[alert.severity]}`}>
            <div className="flex items-start gap-3">
              <span className="text-2xl">{severityIcons[alert.severity]}</span>
              <div className="flex-1">
                <h4 className="font-semibold mb-1">{alert.title}</h4>
                <p className="text-sm">{alert.message}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-lg font-semibold mb-4">ESG Reporting Status</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
            <span className="font-medium">BRSR Compliance</span>
            <span className="text-sm bg-green-600 text-white px-3 py-1 rounded-full">Ready</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-amber-50 rounded-lg">
            <span className="font-medium">GHG Scope 3 Data</span>
            <span className="text-sm bg-amber-600 text-white px-3 py-1 rounded-full">Incomplete</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
            <span className="font-medium">CDP Disclosure</span>
            <span className="text-sm bg-green-600 text-white px-3 py-1 rounded-full">On Track</span>
          </div>
        </div>
      </div>
    </div>
  );
}
