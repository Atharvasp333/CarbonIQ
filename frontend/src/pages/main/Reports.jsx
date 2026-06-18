import { useState, useEffect } from 'react';
import { Download, Calendar, Filter, TrendingUp, DollarSign, Zap } from 'lucide-react';
import { BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import toast from 'react-hot-toast';

const COLORS = ['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444', '#EC4899', '#6366F1', '#14B8A6'];

export default function Reports() {
  const [analysisData, setAnalysisData] = useState(null);
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [serviceFilter, setServiceFilter] = useState('all');
  const [regionFilter, setRegionFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalysisData();
  }, []);

  const loadAnalysisData = () => {
    try {
      const storedData = localStorage.getItem('awsAnalysisData');
      if (storedData) {
        const data = JSON.parse(storedData);
        setAnalysisData(data);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error loading analysis data:', error);
      setLoading(false);
    }
  };

  const handleExportPDF = () => {
    toast.success('PDF export started');
    // TODO: Implement PDF export
  };

  const handleExportCSV = () => {
    if (!analysisData || !analysisData.all_records) {
      toast.error('No data available to export');
      return;
    }

    // Create CSV content
    const headers = ['Service', 'Region', 'Timestamp', 'Energy (kWh)', 'Emissions (kg CO2)', 'Cost ($)', 'Carbon Intensity (gCO2/kWh)'];
    const rows = analysisData.all_records.map(record => [
      record.service,
      record.region,
      record.timestamp,
      record.energy_kwh?.toFixed(4) || '0',
      record.emissions_kg?.toFixed(4) || '0',
      record.cost?.toFixed(4) || '0',
      record.carbon_intensity?.toFixed(2) || '0'
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `carboniq-report-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    
    toast.success('CSV exported successfully');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  if (!analysisData || !analysisData.analytics) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-600 mt-2">Analyze your carbon intensity history and trends</p>
        </div>
        
        <div className="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-8 text-center">
          <TrendingUp className="w-16 h-16 text-yellow-600 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">No Data Available</h3>
          <p className="text-gray-600 mb-4">
            Upload a CUR report or connect your AWS account from the Home page to see analytics and reports.
          </p>
        </div>
      </div>
    );
  }

  const { analytics, summary } = analysisData;

  // Prepare chart data
  const serviceChartData = analytics.by_service?.slice(0, 10).map(s => ({
    name: s.service.replace('Amazon ', '').replace(' Service', ''),
    emissions: parseFloat(s.co2_kg.toFixed(2)),
    cost: parseFloat(s.cost.toFixed(2))
  })) || [];

  const regionChartData = analytics.by_region?.map(r => ({
    name: r.region,
    emissions: parseFloat(r.co2_kg.toFixed(2)),
    value: parseFloat(r.co2_kg.toFixed(2))
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-600 mt-2">Analyze your carbon intensity history and trends</p>
        </div>
        <div className="flex gap-3 mt-4 sm:mt-0">
          <button
            onClick={handleExportPDF}
            className="flex items-center px-4 py-2 bg-white border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            <Download size={18} className="mr-2" />
            Export PDF
          </button>
          <button
            onClick={handleExportCSV}
            className="flex items-center px-4 py-2 bg-gradient-to-r from-emerald-600 to-green-600 text-white rounded-lg hover:from-emerald-700 hover:to-green-700 transition-colors font-medium shadow-lg"
          >
            <Download size={18} className="mr-2" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Analytics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-red-500 to-orange-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-sm font-medium opacity-90">Total Emissions</p>
          <p className="text-3xl font-bold mt-1">{summary.total_emissions_kg?.toFixed(2) || '0'}</p>
          <p className="text-xs opacity-75 mt-1">kg CO₂</p>
        </div>

        <div className="bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <Zap className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-sm font-medium opacity-90">Average Intensity</p>
          <p className="text-3xl font-bold mt-1">{analytics.avg_carbon_intensity?.toFixed(0) || '0'}</p>
          <p className="text-xs opacity-75 mt-1">gCO₂/kWh</p>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-sm font-medium opacity-90">Total Cost</p>
          <p className="text-3xl font-bold mt-1">${summary.total_cost?.toFixed(2) || '0'}</p>
          <p className="text-xs opacity-75 mt-1">USD</p>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <Zap className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-sm font-medium opacity-90">Energy Usage</p>
          <p className="text-3xl font-bold mt-1">{summary.total_energy_kwh?.toFixed(2) || '0'}</p>
          <p className="text-xs opacity-75 mt-1">kWh</p>
        </div>
      </div>

      {/* Top Services and Regions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-2">Top Service</h3>
          <p className="text-2xl font-bold text-emerald-600">{summary.top_service || 'N/A'}</p>
          <p className="text-sm text-gray-600 mt-1">Highest emissions contributor</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-2">Top Region</h3>
          <p className="text-2xl font-bold text-blue-600">{summary.top_region || 'N/A'}</p>
          <p className="text-sm text-gray-600 mt-1">Highest emissions region</p>
        </div>
      </div>

      {/* Emissions by Service Chart */}
      <div className="bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Emissions by Service (Top 10)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={serviceChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="emissions" fill="#10B981" name="Emissions (kg CO₂)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Regional Distribution */}
      <div className="bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Regional Emissions Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={regionChartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {regionChartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Cost vs Emissions Chart */}
      <div className="bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Cost vs Emissions by Service</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={serviceChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Bar yAxisId="left" dataKey="emissions" fill="#10B981" name="Emissions (kg CO₂)" />
            <Bar yAxisId="right" dataKey="cost" fill="#3B82F6" name="Cost ($)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Optimization Opportunities */}
      {analysisData.optimization && analysisData.optimization.opportunities && analysisData.optimization.opportunities.length > 0 && (
        <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl border-2 border-yellow-300 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">💡 Optimization Opportunities</h3>
          <div className="space-y-3">
            {analysisData.optimization.opportunities.slice(0, 5).map((opp, idx) => (
              <div key={idx} className="bg-white rounded-lg p-4 border border-yellow-200">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-gray-900">{opp.title}</p>
                    <p className="text-sm text-gray-600 mt-1">{opp.description}</p>
                  </div>
                  <span className="text-emerald-600 font-bold text-sm whitespace-nowrap ml-4">
                    {opp.potential_reduction_kg?.toFixed(2)} kg CO₂
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
