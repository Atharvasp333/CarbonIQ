export default function ApplianceBreakdown({ breakdown }) {
  if (!breakdown) return null;

  const icons = {
    AC: '❄️',
    Lighting: '💡',
    Servers: '🖥️',
    Others: '📦'
  };

  const getColor = (appliance, isTop) => {
    if (isTop) return 'bg-red-500';
    const colors = { AC: 'bg-blue-500', Lighting: 'bg-green-600', Servers: 'bg-blue-600', Others: 'bg-gray-500' };
    return colors[appliance] || 'bg-gray-500';
  };

  const topAppliance = breakdown.reduce((max, item) => item.co2_kg > max.co2_kg ? item : max, breakdown[0]);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 className="text-lg font-semibold mb-4">Appliance Breakdown</h3>
      <div className="space-y-4">
        {breakdown.map((item, idx) => (
          <div key={idx}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{icons[item.appliance]}</span>
                <span className="font-medium">{item.appliance}</span>
              </div>
              <div className="text-right">
                <div className="font-semibold">{item.co2_kg.toFixed(2)} kg</div>
                <div className="text-sm text-gray-500">{item.percentage.toFixed(1)}%</div>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full ${getColor(item.appliance, item.appliance === topAppliance.appliance)}`}
                style={{ width: `${item.percentage}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
