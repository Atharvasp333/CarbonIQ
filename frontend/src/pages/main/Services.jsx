import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Server, Database, HardDrive, Zap, Cloud, Box, TrendingUp, DollarSign } from 'lucide-react';

const serviceIcons = {
  'Amazon Elastic Compute Cloud': Server,
  'EC2': Server,
  'Amazon Relational Database Service': Database,
  'RDS': Database,
  'Amazon Simple Storage Service': HardDrive,
  'S3': HardDrive,
  'AWS Lambda': Zap,
  'Lambda': Zap,
  'Amazon CloudFront': Cloud,
  'CloudFront': Cloud,
  'Amazon Elastic Block Store': Box,
  'EBS': Box,
};

const serviceColors = {
  'Amazon Elastic Compute Cloud': 'bg-blue-500',
  'EC2': 'bg-blue-500',
  'Amazon Relational Database Service': 'bg-purple-500',
  'RDS': 'bg-purple-500',
  'Amazon Simple Storage Service': 'bg-green-500',
  'S3': 'bg-green-500',
  'AWS Lambda': 'bg-yellow-500',
  'Lambda': 'bg-yellow-500',
  'Amazon CloudFront': 'bg-indigo-500',
  'CloudFront': 'bg-indigo-500',
  'Amazon Elastic Block Store': 'bg-red-500',
  'EBS': 'bg-red-500',
};

export default function Services() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalEmissions, setTotalEmissions] = useState(0);
  const [totalCost, setTotalCost] = useState(0);

  useEffect(() => {
    loadServicesData();
  }, []);

  const loadServicesData = () => {
    try {
      const storedData = localStorage.getItem('awsAnalysisData');
      if (!storedData) {
        setLoading(false);
        return;
      }

      const analysisData = JSON.parse(storedData);
      
      if (analysisData.analytics && analysisData.analytics.by_service) {
        // Transform analytics data to services format
        const servicesData = analysisData.analytics.by_service.map(service => ({
          name: service.service,
          emissions: service.co2_kg,
          cost: service.cost,
          energy: service.energy_kwh,
          intensity: service.avg_carbon_intensity,
          records: service.record_count,
        }));

        setServices(servicesData);
        setTotalEmissions(analysisData.summary.total_emissions_kg || 0);
        setTotalCost(analysisData.summary.total_cost || 0);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error loading services data:', error);
      setLoading(false);
    }
  };

  const getServiceIcon = (serviceName) => {
    const Icon = serviceIcons[serviceName] || Server;
    return Icon;
  };

  const getServiceColor = (serviceName) => {
    return serviceColors[serviceName] || 'bg-gray-500';
  };

  const formatServiceName = (name) => {
    // Shorten long AWS service names
    return name.replace('Amazon ', '').replace(' Service', '');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  if (services.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Services</h1>
          <p className="text-gray-600 mt-2">Monitor carbon intensity across your AWS services</p>
        </div>
        
        <div className="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-8 text-center">
          <Server className="w-16 h-16 text-yellow-600 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">No Data Available</h3>
          <p className="text-gray-600 mb-4">
            Upload a CUR report or connect your AWS account from the Home page to see service analytics.
          </p>
          <Link
            to="/"
            className="inline-block px-6 py-3 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white font-semibold rounded-lg transition-all"
          >
            Go to Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Services</h1>
        <p className="text-gray-600 mt-2">Monitor carbon intensity across your AWS services</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-emerald-100 text-sm font-medium">Total Services</p>
              <p className="text-3xl font-bold mt-1">{services.length}</p>
            </div>
            <Server className="w-12 h-12 text-emerald-100 opacity-50" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Total Emissions</p>
              <p className="text-3xl font-bold mt-1">{totalEmissions.toFixed(2)}</p>
              <p className="text-blue-100 text-xs mt-1">kg CO₂</p>
            </div>
            <TrendingUp className="w-12 h-12 text-blue-100 opacity-50" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">Total Cost</p>
              <p className="text-3xl font-bold mt-1">${totalCost.toFixed(2)}</p>
            </div>
            <DollarSign className="w-12 h-12 text-purple-100 opacity-50" />
          </div>
        </div>
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {services.map((service, index) => {
          const Icon = getServiceIcon(service.name);
          const colorClass = getServiceColor(service.name);
          const displayName = formatServiceName(service.name);
          
          return (
            <Link
              key={index}
              to={`/service/${encodeURIComponent(service.name)}`}
              className="group bg-white rounded-xl shadow-sm border-2 border-gray-200 p-6 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 hover:border-emerald-300"
            >
              <div className="flex items-start justify-between">
                <div className={`${colorClass} p-3 rounded-lg`}>
                  <Icon size={24} className="text-white" />
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">Carbon Intensity</p>
                  <p className="text-lg font-bold text-gray-900">{service.intensity?.toFixed(0) || 'N/A'}</p>
                  <p className="text-xs text-gray-500">gCO₂/kWh</p>
                </div>
              </div>
              
              <h3 className="text-xl font-bold text-gray-900 mt-4 group-hover:text-emerald-600 transition-colors">
                {displayName}
              </h3>
              
              <div className="mt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Emissions:</span>
                  <span className="font-semibold text-gray-900">{service.emissions.toFixed(2)} kg CO₂</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Cost:</span>
                  <span className="font-semibold text-gray-900">${service.cost.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Energy:</span>
                  <span className="font-semibold text-gray-900">{service.energy.toFixed(2)} kWh</span>
                </div>
              </div>
              
              <div className="mt-4 flex items-center text-emerald-600 font-medium text-sm">
                View Details
                <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
