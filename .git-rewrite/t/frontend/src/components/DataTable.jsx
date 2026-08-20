function DataTable({ data }) {
  if (!data || data.length === 0) {
    return null;
  }

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
      <h3 className="text-lg font-semibold text-white mb-4">Detailed Line Items</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left py-3 px-4 text-slate-300 font-medium">Service</th>
              <th className="text-left py-3 px-4 text-slate-300 font-medium">Region</th>
              <th className="text-left py-3 px-4 text-slate-300 font-medium">Instance Type</th>
              <th className="text-right py-3 px-4 text-slate-300 font-medium">Usage</th>
              <th className="text-right py-3 px-4 text-slate-300 font-medium">Cost ($)</th>
              <th className="text-right py-3 px-4 text-slate-300 font-medium">CO₂ (kg)</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, idx) => (
              <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition">
                <td className="py-3 px-4 text-white">{item.service}</td>
                <td className="py-3 px-4 text-slate-300">{item.region}</td>
                <td className="py-3 px-4 text-slate-300">{item.instance_type || '-'}</td>
                <td className="py-3 px-4 text-right text-slate-300">{item.usage_amount.toFixed(2)}</td>
                <td className="py-3 px-4 text-right text-green-400">{item.cost.toFixed(2)}</td>
                <td className="py-3 px-4 text-right text-red-400">{item.co2_kg.toFixed(4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DataTable;
