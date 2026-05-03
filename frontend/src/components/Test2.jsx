import { useState, useEffect } from 'react';

const ZONES = {
  "India": [
    { code: "IN", name: "Mainland India" },
    { code: "IN-EA", name: "East India" },
    { code: "IN-WE", name: "West India" },
    { code: "IN-SO", name: "South India" },
    { code: "IN-NO", name: "North India" }
  ],
  "USA": [
    { code: "US-CAL-CISO", name: "California" },
    { code: "US-TEX-ERCO", name: "Texas" },
    { code: "US-MIDA-PJM", name: "Mid-Atlantic" }
  ],
  "Europe": [
    { code: "FR", name: "France" },
    { code: "DE", name: "Germany" },
    { code: "GB", name: "United Kingdom" },
    { code: "NO", name: "Norway" }
  ]
};

function Test2() {
  const [zone, setZone] = useState('IN-EA');
  const [datetime, setDatetime] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Set current UTC datetime on mount
    const now = new Date();
    const year = now.getUTCFullYear();
    const month = String(now.getUTCMonth() + 1).padStart(2, '0');
    const day = String(now.getUTCDate()).padStart(2, '0');
    const hours = String(now.getUTCHours()).padStart(2, '0');
    const minutes = String(now.getUTCMinutes()).padStart(2, '0');
    setDatetime(`${year}-${month}-${day} ${hours}:${minutes}`);
  }, []);

  const fetchData = async () => {
    if (!zone || !datetime) {
      setError('Please select a zone and enter datetime');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(
        `http://localhost:8000/api/electricity/test?zone=${encodeURIComponent(zone)}&datetime=${encodeURIComponent(datetime)}`
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'API request failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">CarbonIQ</h1>
          <p className="text-gray-600">Electricity Maps API Test</p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">
            Electricity Maps Test
          </h2>

          {/* Input Section */}
          <div className="space-y-6 mb-8">
            {/* Zone Dropdown */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Region (Zone)
              </label>
              <select
                value={zone}
                onChange={(e) => setZone(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                {Object.entries(ZONES).map(([region, zones]) => (
                  <optgroup key={region} label={region}>
                    {zones.map((z) => (
                      <option key={z.code} value={z.code}>
                        {z.name} ({z.code})
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>

            {/* Datetime Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Datetime (YYYY-MM-DD HH:MM)
              </label>
              <input
                type="text"
                value={datetime}
                onChange={(e) => setDatetime(e.target.value)}
                placeholder="2026-05-02 04:22"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                Auto-filled with current UTC time
              </p>
            </div>

            {/* Fetch Button */}
            <button
              onClick={fetchData}
              disabled={loading}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Fetching Data...
                </>
              ) : (
                'Fetch Data'
              )}
            </button>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 font-medium">Error:</p>
              <p className="text-red-600">{error}</p>
            </div>
          )}

          {/* Result Display */}
          {result && (
            <div className="space-y-6">
              {/* Formatted Result */}
              <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 border border-green-200">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                  Carbon Intensity Data
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <p className="text-sm text-gray-600 mb-1">Zone</p>
                    <p className="text-xl font-bold text-gray-800">{result.zone}</p>
                  </div>
                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <p className="text-sm text-gray-600 mb-1">Timestamp</p>
                    <p className="text-xl font-bold text-gray-800">
                      {new Date(result.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <p className="text-sm text-gray-600 mb-1">Carbon Intensity</p>
                    <p className="text-2xl font-bold text-green-600">
                      {result.carbon_intensity} <span className="text-sm">gCO₂/kWh</span>
                    </p>
                  </div>
                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <p className="text-sm text-gray-600 mb-1">Life Cycle</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {result.carbon_intensity_lifecycle} <span className="text-sm">gCO₂/kWh</span>
                    </p>
                  </div>
                </div>
              </div>

              {/* Raw JSON Response */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3">
                  Raw JSON Response (Debug)
                </h3>
                <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                  <pre className="text-green-400 text-sm font-mono">
                    {JSON.stringify(result.raw_response, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Info Footer */}
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>This test page verifies Electricity Maps API integration</p>
          <p className="mt-1">Data will be used for carbon optimization in the main system</p>
        </div>
      </div>
    </div>
  );
}

export default Test2;
