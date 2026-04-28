function MetricsBar({ data }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="bg-gradient-to-br from-red-500/20 to-red-600/20 backdrop-blur-sm rounded-xl p-6 border border-red-500/30">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-red-300 text-sm font-medium">Total CO₂ Emissions</p>
            <p className="text-3xl font-bold text-white mt-1">{data.total_co2_kg}</p>
            <p className="text-red-200 text-xs mt-1">kg CO₂</p>
          </div>
          <div className="text-4xl">🌍</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 backdrop-blur-sm rounded-xl p-6 border border-green-500/30">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-green-300 text-sm font-medium">Total Cost</p>
            <p className="text-3xl font-bold text-white mt-1">${data.total_cost}</p>
            <p className="text-green-200 text-xs mt-1">USD</p>
          </div>
          <div className="text-4xl">💰</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 backdrop-blur-sm rounded-xl p-6 border border-blue-500/30">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-blue-300 text-sm font-medium">Top Region</p>
            <p className="text-2xl font-bold text-white mt-1">{data.top_region}</p>
            <p className="text-blue-200 text-xs mt-1">Highest emissions</p>
          </div>
          <div className="text-4xl">📍</div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 backdrop-blur-sm rounded-xl p-6 border border-purple-500/30">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-purple-300 text-sm font-medium">Top Service</p>
            <p className="text-2xl font-bold text-white mt-1">{data.top_service}</p>
            <p className="text-purple-200 text-xs mt-1">Most polluting</p>
          </div>
          <div className="text-4xl">☁️</div>
        </div>
      </div>
    </div>
  );
}

export default MetricsBar;
