import { useState, useEffect } from 'react';
import { toast, Toaster } from 'react-hot-toast';

const RegionalTestScreen = () => {
  const [regions, setRegions] = useState([]);
  const [selectedRegion, setSelectedRegion] = useState('IN');
  const [kwh, setKwh] = useState(100);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetchRegions();
  }, []);

  const fetchRegions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/available-regions');
      const data = await response.json();
      setRegions(data.regions);
    } catch (error) {
      toast.error('Failed to load regions');
    }
  };

  const testEmission = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/test-regional-emission', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          region_code: selectedRegion,
          kwh: parseFloat(kwh),
        }),
      });

      const data = await response.json();
      setResult(data);

      // Show toast based on source
      if (data.source === 'climatiq') {
        toast.success(
          <div>
            <strong>✓ Climatiq API Success!</strong>
            <p className="text-sm mt-1">{data.message}</p>
          </div>,
          { duration: 4000 }
        );
      } else {
        toast.error(
          <div>
            <strong>⚠ Using Fallback Calculation</strong>
            <p className="text-sm mt-1">{data.message}</p>
          </div>,
          { duration: 4000 }
        );
      }
    } catch (error) {
      toast.error('Failed to test emission calculation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-8">
      <Toaster position="top-right" />
      
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Regional Emission Testing
          </h1>
          <p className="text-gray-600 mb-8">
            Test if Climatiq API is working for different regions or if fallback calculations are being used
          </p>

          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* Region Selection */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Select Region
              </label>
              <select
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                {regions.map((region) => (
                  <option key={region.code} value={region.code}>
                    {region.name} ({region.code}) - {region.factor} kg CO₂/kWh
                  </option>
                ))}
              </select>
            </div>

            {/* kWh Input */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Energy Usage (kWh)
              </label>
              <input
                type="number"
                value={kwh}
                onChange={(e) => setKwh(e.target.value)}
                min="0"
                step="0.1"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Enter kWh"
              />
            </div>
          </div>

          {/* Test Button */}
          <button
            onClick={testEmission}
            disabled={loading}
            className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 rounded-lg hover:from-green-600 hover:to-blue-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Testing...' : 'Test Emission Calculation'}
          </button>

          {/* Results */}
          {result && (
            <div className="mt-8 bg-gray-50 rounded-xl p-6 border-2 border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-800">Test Results</h2>
                <span
                  className={`px-4 py-2 rounded-full text-sm font-semibold ${
                    result.source === 'climatiq'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-orange-100 text-orange-700'
                  }`}
                >
                  {result.source === 'climatiq' ? '✓ Climatiq API' : '⚠ Fallback'}
                </span>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Region</p>
                  <p className="text-lg font-bold text-gray-800">
                    {result.region_name} ({result.region_code})
                  </p>
                </div>

                <div className="bg-white p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Energy Usage</p>
                  <p className="text-lg font-bold text-gray-800">{result.kwh} kWh</p>
                </div>

                <div className="bg-white p-4 rounded-lg">
                  <p className="text-sm text-gray-600">CO₂ Emissions</p>
                  <p className="text-lg font-bold text-green-600">{result.co2_kg} kg</p>
                </div>

                <div className="bg-white p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Emission Factor</p>
                  <p className="text-lg font-bold text-gray-800">
                    {result.emission_factor} kg/kWh
                  </p>
                </div>
              </div>

              <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-blue-800">
                  <strong>Message:</strong> {result.message}
                </p>
              </div>
            </div>
          )}

          {/* Region Reference Table */}
          <div className="mt-8">
            <h3 className="text-lg font-bold text-gray-800 mb-4">Available Regions</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-2 text-left">Code</th>
                    <th className="px-4 py-2 text-left">Region</th>
                    <th className="px-4 py-2 text-left">Type</th>
                    <th className="px-4 py-2 text-right">Factor (kg CO₂/kWh)</th>
                  </tr>
                </thead>
                <tbody>
                  {regions.map((region, idx) => (
                    <tr
                      key={region.code}
                      className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                    >
                      <td className="px-4 py-2 font-mono font-semibold">{region.code}</td>
                      <td className="px-4 py-2">{region.name}</td>
                      <td className="px-4 py-2 text-gray-600">{region.type}</td>
                      <td className="px-4 py-2 text-right font-semibold">
                        {region.factor}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegionalTestScreen;
