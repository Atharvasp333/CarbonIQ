import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, TrendingDown, TrendingUp, Activity } from 'lucide-react';

export default function ServiceDetail() {
  const { serviceName } = useParams();
  
  const serviceExists = ['ec2', 'rds', 's3', 'lambda', 'cloudfront', 'ebs'].includes(serviceName?.toLowerCase());

  if (!serviceExists) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Service Not Found</h1>
          <p className="text-gray-600 mb-8">The service you're looking for doesn't exist.</p>
          <Link
            to="/services"
            className="inline-flex items-center px-6 py-3 bg-[#2D6A4F] text-white rounded-lg hover:bg-[#1B4332] transition-colors"
          >
            <ArrowLeft size={20} className="mr-2" />
            Back to Services
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Link
          to="/services"
          className="inline-flex items-center text-[#2D6A4F] hover:text-[#1B4332] mb-4"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Services
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 capitalize">{serviceName}</h1>
        <p className="text-gray-600 mt-2">Detailed carbon intensity analytics</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Current Intensity</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">420 gCO₂/kWh</p>
            </div>
            <Activity className="text-blue-500" size={32} />
          </div>
          <p className="text-sm text-green-600 mt-2">↓ 5% from average</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Emissions</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">145.8 kg</p>
            </div>
            <TrendingUp className="text-red-500" size={32} />
          </div>
          <p className="text-sm text-red-600 mt-2">↑ 12% from last month</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Energy Usage</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">347 kWh</p>
            </div>
            <TrendingDown className="text-green-500" size={32} />
          </div>
          <p className="text-sm text-green-600 mt-2">↓ 3% from last month</p>
        </div>
      </div>

      {/* Historical Graph */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Historical Trends</h2>
        <div className="h-80 flex items-center justify-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <p className="text-gray-500">Historical trend chart will be displayed here</p>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Carbon Impact & Recommendations</h2>
        <div className="space-y-4">
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h3 className="font-semibold text-green-900">✓ Good Practice</h3>
            <p className="text-sm text-green-700 mt-1">Your {serviceName} usage is optimized for off-peak hours</p>
          </div>
          <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <h3 className="font-semibold text-yellow-900">⚠ Consider</h3>
            <p className="text-sm text-yellow-700 mt-1">Moving workloads to us-west-2 could reduce emissions by 30%</p>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="font-semibold text-blue-900">💡 Tip</h3>
            <p className="text-sm text-blue-700 mt-1">Enable auto-scaling to match demand and reduce waste</p>
          </div>
        </div>
      </div>
    </div>
  );
}
