import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Activity, Zap, DollarSign, MapPin, Clock, ChevronDown, ChevronUp } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

export default function ServiceDetail() {
  const { serviceName } = useParams();
  const [serviceData, setServiceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedTime, setExpandedTime] = useState(null);

  useEffect(() => {
    loadServiceData();
  }, [serviceName]);

  const loadServiceData = () => {
    try {
      const storedData = localStorage.getItem('awsAnalysisData');
      if (!storedData) {
        setLoading(false);
        return;
      }

      const analysisData = JSON.parse(storedData);
      const allRecords = analysisData.all_records || [];
      
      // Decode the service name from URL
      const decodedServiceName = decodeURIComponent(serviceName);
      
      // Filter records for this specific service
      const serviceRecords = allRecords.filter(r => r.service === decodedServiceName);
      
      if (serviceRecords.length === 0) {
        setLoading(false);
        return;
      }

      // Calculate service totals
      const totalEmissions = serviceRecords.reduce((sum, r) => sum + (r.emissions_kg || 0), 0);
      const totalCost = serviceRecords.reduce((sum, r) => sum + (r.cost || 0), 0);
      const totalEnergy = serviceRecords.reduce((sum, r) => sum + (r.energy_kwh || 0), 0);
      const avgIntensity = serviceRecords.reduce((sum, r) => sum + (r.carbon_intensity || 0), 0) / serviceRecords.length;

      // Group by region
      const byRegion = {};
      serviceRecords.forEach(record => {
        const region = record.region || 'Unknown';
        if (!byRegion[region]) {
          byRegion[region] = {
            region,
            emissions_kg: 0,
            cost: 0,
            energy_kwh: 0,
            count: 0,
            intensities: []
          };
        }
        byRegion[region].emissions_kg += record.emissions_kg || 0;
        byRegion[region].cost += record.cost || 0;
        byRegion[region].energy_kwh += record.energy_kwh || 0;
        byRegion[region].count += 1;
        byRegion[region].intensities.push(record.carbon_intensity || 0);
      });

      const regionBreakdown = Object.values(byRegion).map(r => ({
        ...r,
        avg_carbon_intensity: r.intensities.reduce((a, b) => a + b, 0) / r.intensities.length
      })).sort((a, b) => b.emissions_kg - a.emissions_kg);

      // Group by time (with full timestamp and carbon intensity)
      const byTime = {};
      serviceRecords.forEach(record => {
        if (!record.timestamp) return;
        try {
          const dt = new Date(record.timestamp);
          const timeKey = record.timestamp; // Keep full timestamp as key
          const displayTime = `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')} ${String(dt.getHours()).padStart(2, '0')}:${String(dt.getMinutes()).padStart(2, '0')}`;
          
          if (!byTime[timeKey]) {
            byTime[timeKey] = {
              timestamp: record.timestamp,
              displayTime: displayTime,
              emissions_kg: 0,
              cost: 0,
              energy_kwh: 0,
              carbon_intensity: record.carbon_intensity || 0, // Actual intensity for this time
              region: record.region,
              zone: record.zone,
              count: 0,
              records: []
            };
          }
          byTime[timeKey].emissions_kg += record.emissions_kg || 0;
          byTime[timeKey].cost += record.cost || 0;
          byTime[timeKey].energy_kwh += record.energy_kwh || 0;
          byTime[timeKey].count += 1;
          byTime[timeKey].records.push({
            resource_id: record.resource_id,
            region: record.region,
            zone: record.zone,
            emissions_kg: record.emissions_kg,
            carbon_intensity: record.carbon_intensity,
            energy_kwh: record.energy_kwh,
            cost: record.cost
          });
        } catch (e) {
          // Skip invalid timestamps
        }
      });

      const timeSeries = Object.values(byTime).sort((a, b) => 
        a.timestamp.localeCompare(b.timestamp)
      );

      setServiceData({
        name: decodedServiceName,
        totalEmissions,
        totalCost,
        totalEnergy,
        avgIntensity,
        recordCount: serviceRecords.length,
        regionBreakdown,
        timeSeries
      });
      
      setLoading(false);
    } catch (error) {
      console.error('Error loading service data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  if (!serviceData) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Service Not Found</h1>
          <p className="text-gray-600 mb-8">No data available for this service.</p>
          <Link
            to="/services"
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-emerald-600 to-green-600 text-white rounded-lg hover:from-emerald-700 hover:to-green-700 transition-colors"
          >
            <ArrowLeft size={20} className="mr-2" />
            Back to Services
          </Link>
        </div>
      </div>
    );
  }

  const regionChartData = serviceData.regionBreakdown.map(r => ({
    name: r.region,
    emissions: parseFloat(r.emissions_kg.toFixed(2)),
    cost: parseFloat(r.cost.toFixed(2))
  }));

  const timeChartData = serviceData.timeSeries.map(t => ({
    time: t.displayTime,
    emissions: parseFloat(t.emissions_kg.toFixed(2)),
    intensity: parseFloat(t.carbon_intensity.toFixed(0)),
    cost: parseFloat(t.cost.toFixed(2))
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Link
          to="/services"
          className="inline-flex items-center text-emerald-600 hover:text-emerald-700 mb-4 font-medium"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Services
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">{serviceData.name}</h1>
        <p className="text-gray-600 mt-2">Detailed carbon emissions analysis by region and time</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <div className="bg-gradient-to-br from-red-500 to-orange-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <Activity className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-sm font-medium opacity-90">Total Emissions</p>
          <p className="text-3xl font-bold mt-1">{serviceData.totalEmissions.toFixed(2)}</p>
          <p className="text-xs opacity-75 mt-1">kg CO₂</p>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-3xl font-bold mt-1">${serviceData.totalCost.toFixed(2)}</p>
          <p className="text-xs opacity-75 mt-1">USD</p>
        </div>

        <div className="bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <Zap className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-sm font-medium opacity-90">Avg Intensity</p>
          <p className="text-3xl font-bold mt-1">{serviceData.avgIntensity.toFixed(0)}</p>
          <p className="text-xs opacity-75 mt-1">gCO₂/kWh</p>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <Zap className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-sm font-medium opacity-90">Energy Usage</p>
          <p className="text-3xl font-bold mt-1">{serviceData.totalEnergy.toFixed(2)}</p>
          <p className="text-xs opacity-75 mt-1">kWh</p>
        </div>

        <div className="bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <Clock className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-sm font-medium opacity-90">Time Periods</p>
          <p className="text-3xl font-bold mt-1">{serviceData.timeSeries.length}</p>
          <p className="text-xs opacity-75 mt-1">unique timestamps</p>
        </div>
      </div>

      {/* Regional Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <MapPin className="w-5 h-5 text-emerald-600 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Emissions by Region</h3>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={regionChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="emissions" fill="#10B981" name="Emissions (kg CO₂)" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <MapPin className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Regional Distribution</h3>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={regionChartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="emissions"
              >
                {regionChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `${value.toFixed(2)} kg CO₂`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Time Series */}
      {timeChartData.length > 0 && (
        <>
          <div className="bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6">
            <div className="flex items-center mb-4">
              <Clock className="w-5 h-5 text-purple-600 mr-2" />
              <h3 className="text-lg font-bold text-gray-900">Emissions & Carbon Intensity Over Time</h3>
            </div>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={timeChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="time" 
                  angle={-45} 
                  textAnchor="end" 
                  height={100}
                  tick={{ fontSize: 11 }}
                />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                    borderRadius: '8px'
                  }}
                  labelStyle={{ color: '#e2e8f0' }}
                  itemStyle={{ color: '#e2e8f0' }}
                />
                <Legend />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="emissions" 
                  stroke="#8b5cf6" 
                  name="Emissions (kg CO₂)" 
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
                <Line 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="intensity" 
                  stroke="#f59e0b" 
                  name="Carbon Intensity (gCO₂/kWh)" 
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Detailed Time-based Breakdown Table */}
          <div className="bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-900">Detailed Time-based Breakdown</h3>
              <span className="text-sm text-gray-600">{serviceData.timeSeries.length} unique timestamps</span>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Region</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Zone</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Carbon Intensity</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Emissions</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Energy</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cost</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Records</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {serviceData.timeSeries.map((timePoint, idx) => (
                    <>
                      <tr key={idx} className="hover:bg-gray-50 cursor-pointer" onClick={() => setExpandedTime(expandedTime === idx ? null : idx)}>
                        <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                          <div className="flex items-center">
                            {expandedTime === idx ? <ChevronUp size={16} className="mr-2 text-gray-400" /> : <ChevronDown size={16} className="mr-2 text-gray-400" />}
                            {timePoint.displayTime}
                          </div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                          {timePoint.region}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 font-mono">
                          {timePoint.zone}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            timePoint.carbon_intensity < 100 ? 'bg-green-100 text-green-800' :
                            timePoint.carbon_intensity < 300 ? 'bg-yellow-100 text-yellow-800' :
                            timePoint.carbon_intensity < 500 ? 'bg-orange-100 text-orange-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {timePoint.carbon_intensity.toFixed(0)} gCO₂/kWh
                          </span>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 font-semibold">
                          {timePoint.emissions_kg.toFixed(4)} kg CO₂
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                          {timePoint.energy_kwh.toFixed(4)} kWh
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                           ${timePoint.cost.toFixed(4)}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                          {timePoint.count}
                        </td>
                      </tr>
                      {/* Expanded details */}
                      {expandedTime === idx && (
                        <tr>
                          <td colSpan="8" className="px-4 py-3 bg-gray-50">
                            <div className="ml-8 border-l-4 border-blue-500 pl-4">
                              <h4 className="text-sm font-semibold text-gray-900 mb-2">Individual Records ({timePoint.records.length})</h4>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                {timePoint.records.map((record, recIdx) => (
                                  <div key={recIdx} className="bg-white border border-gray-200 rounded-lg p-3 text-xs">
                                    <div className="flex items-center justify-between mb-2">
                                      <span className="font-mono text-gray-600">{record.resource_id || 'N/A'}</span>
                                      <span className="text-gray-500">{record.region}</span>
                                    </div>
                                    <div className="grid grid-cols-2 gap-2">
                                      <div>
                                        <span className="text-gray-500">Zone:</span>
                                        <span className="ml-1 font-mono">{record.zone}</span>
                                      </div>
                                      <div>
                                        <span className="text-gray-500">Intensity:</span>
                                        <span className="ml-1 font-semibold">{record.carbon_intensity.toFixed(0)}</span>
                                      </div>
                                      <div>
                                        <span className="text-gray-500">Emissions:</span>
                                        <span className="ml-1 font-semibold text-red-600">{record.emissions_kg.toFixed(4)} kg</span>
                                      </div>
                                      <div>
                                        <span className="text-gray-500">Energy:</span>
                                        <span className="ml-1">{record.energy_kwh.toFixed(4)} kWh</span>
                                      </div>
                                      <div>
                                        <span className="text-gray-500">Cost:</span>
                                         <span className="ml-1">${record.cost.toFixed(4)}</span>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  ))}
                </tbody>
              </table>
            </div>
            
            {/* Info about carbon intensity fetching */}
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-800">Real-time Carbon Intensity Data</h3>
                  <p className="mt-1 text-sm text-blue-700">
                    Each timestamp shows the actual carbon intensity fetched from Electricity Maps API for that specific date, time, and region. 
                    Different timestamps have different carbon intensities based on the grid's energy mix at that moment.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Regional Details Table */}
      <div className="bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Regional Breakdown Details</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Region</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Emissions (kg CO₂)</th>
                 <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cost ($)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Energy (kWh)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Intensity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Records</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {serviceData.regionBreakdown.map((region, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{region.region}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{region.emissions_kg.toFixed(2)}</td>
                   <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${region.cost.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{region.energy_kwh.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{region.avg_carbon_intensity.toFixed(0)} gCO₂/kWh</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{region.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
