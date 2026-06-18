import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

function TrendChart({ data, title, dataKey = 'region' }) {
  // Handle missing or empty data
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
        <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
        <div className="flex items-center justify-center h-[300px] text-slate-400">
          No data available
        </div>
      </div>
    );
  }

  const chartData = data.map(item => ({
    name: item[dataKey] || item.region || item.service,
    co2_kg: item.co2_kg || item.emissions_kg,
    cost: item.cost
  }));

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
      <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
          <XAxis
            dataKey="name"
            stroke="#94a3b8"
            tick={{ fill: '#cbd5e1' }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis stroke="#94a3b8" tick={{ fill: '#cbd5e1' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '8px',
              color: '#fff'
            }}
            formatter={(value, name) => [
              name === 'co2_kg' ? `${value} kg CO₂` : `$${value}`,
              name === 'co2_kg' ? 'Emissions' : 'Cost'
            ]}
          />
          <Legend
            wrapperStyle={{ color: '#fff' }}
            formatter={(value) => (
              <span style={{ color: '#cbd5e1' }}>
                {value === 'co2_kg' ? 'CO₂ Emissions' : 'Cost'}
              </span>
            )}
          />
          <Bar dataKey="co2_kg" fill="#3b82f6" />
          <Bar dataKey="cost" fill="#10b981" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TrendChart;
