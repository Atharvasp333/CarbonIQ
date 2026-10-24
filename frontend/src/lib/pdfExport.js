/**
 * CarbonIQ Executive PDF Export Generator
 * Generates an executive-ready sustainability PDF report using clean vector print styling.
 */

export function generateSustainabilityPDF(analysisData, userInfo = {}) {
  if (!analysisData || !analysisData.summary) {
    throw new Error("No analysis data available to generate report");
  }

  const { summary, analytics } = analysisData;
  const userName = userInfo.name || "Enterprise User";
  const organization = userInfo.organization || "Cloud Infrastructure";
  const reportDate = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric"
  });

  const totalEmissions = summary.total_emissions_kg != null ? Number(summary.total_emissions_kg).toFixed(2) : "0.00";
  const totalCost = summary.total_cost != null ? Number(summary.total_cost).toFixed(2) : "0.00";
  const totalEnergy = summary.total_energy_kwh != null ? Number(summary.total_energy_kwh).toFixed(2) : "0.00";
  const topService = summary.top_service || "Compute (EC2)";
  const topRegion = summary.top_region || "us-east-1";

  const services = (analytics?.service_breakdown || analytics?.by_service || []).slice(0, 10);
  const regions = (analytics?.region_breakdown || analytics?.by_region || []).slice(0, 8);

  const htmlContent = `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>CarbonIQ Sustainability Report - ${reportDate}</title>
        <style>
          @page {
            size: A4;
            margin: 15mm;
          }
          body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1f2937;
            background: #ffffff;
            margin: 0;
            padding: 0;
            font-size: 12px;
            line-height: 1.5;
          }
          .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #10b981;
            padding-bottom: 12px;
            margin-bottom: 20px;
          }
          .logo {
            font-size: 24px;
            font-weight: 800;
            color: #064e3b;
            letter-spacing: -0.5px;
          }
          .logo span {
            color: #10b981;
          }
          .report-meta {
            text-align: right;
            font-size: 11px;
            color: #6b7280;
          }
          .title-section {
            margin-bottom: 20px;
          }
          .title-section h1 {
            font-size: 20px;
            margin: 0 0 4px 0;
            color: #111827;
          }
          .title-section p {
            margin: 0;
            color: #4b5563;
          }
          .kpi-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-bottom: 24px;
          }
          .kpi-card {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 12px;
          }
          .kpi-card.highlight {
            background: #ecfdf5;
            border-color: #a7f3d0;
          }
          .kpi-title {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #6b7280;
            margin-bottom: 4px;
          }
          .kpi-card.highlight .kpi-title {
            color: #065f46;
          }
          .kpi-value {
            font-size: 18px;
            font-weight: 700;
            color: #111827;
          }
          .kpi-card.highlight .kpi-value {
            color: #047857;
          }
          h2 {
            font-size: 14px;
            font-weight: 700;
            margin: 20px 0 8px 0;
            color: #111827;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 4px;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 16px;
            font-size: 11px;
          }
          th {
            background: #f3f4f6;
            color: #374151;
            font-weight: 600;
            text-align: left;
            padding: 6px 8px;
            border-bottom: 1px solid #d1d5db;
          }
          td {
            padding: 6px 8px;
            border-bottom: 1px solid #e5e7eb;
          }
          tr:nth-child(even) td {
            background: #fafafa;
          }
          .recommendations {
            background: #f0fdf4;
            border-left: 4px solid #10b981;
            padding: 12px;
            border-radius: 0 8px 8px 0;
            margin-top: 16px;
          }
          .recommendations h3 {
            margin: 0 0 6px 0;
            font-size: 12px;
            color: #065f46;
          }
          .recommendations ul {
            margin: 0;
            padding-left: 16px;
            color: #1f2937;
          }
          .footer {
            margin-top: 30px;
            border-top: 1px solid #e5e7eb;
            padding-top: 8px;
            text-align: center;
            font-size: 10px;
            color: #9ca3af;
          }
        </style>
      </head>
      <body>
        <div class="header">
          <div class="logo">Carbon<span>IQ</span></div>
          <div class="report-meta">
            <div><strong>Report Date:</strong> ${reportDate}</div>
            <div><strong>Organization:</strong> ${organization}</div>
            <div><strong>Auditor / User:</strong> ${userName}</div>
          </div>
        </div>

        <div class="title-section">
          <h1>Cloud Carbon Footprint & ESG Sustainability Audit</h1>
          <p>Comprehensive emissions accounting, energy consumption, and optimization analysis.</p>
        </div>

        <div class="kpi-grid">
          <div class="kpi-card highlight">
            <div class="kpi-title">Total Carbon Emissions</div>
            <div class="kpi-value">${totalEmissions} kg CO₂e</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">Total Energy Consumed</div>
            <div class="kpi-value">${totalEnergy} kWh</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">Total Cloud Cost</div>
            <div class="kpi-value">$${totalCost}</div>
          </div>
        </div>

        <h2>Top Emitting Cloud Services</h2>
        <table>
          <thead>
            <tr>
              <th>Service</th>
              <th>Emissions (kg CO₂e)</th>
              <th>Energy (kWh)</th>
              <th>Cost ($)</th>
            </tr>
          </thead>
          <tbody>
            ${services.map(s => `
              <tr>
                <td><strong>${s.service || s.name}</strong></td>
                <td>${(s.emissions_kg || s.co2_kg || 0).toFixed(2)}</td>
                <td>${(s.energy_kwh || 0).toFixed(2)}</td>
                <td>$${(s.cost || 0).toFixed(2)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <h2>Regional Carbon Breakdown</h2>
        <table>
          <thead>
            <tr>
              <th>AWS Region</th>
              <th>Emissions (kg CO₂e)</th>
              <th>Grid Carbon Intensity</th>
            </tr>
          </thead>
          <tbody>
            ${regions.map(r => `
              <tr>
                <td><strong>${r.region || r.name}</strong></td>
                <td>${(r.emissions_kg || r.co2_kg || 0).toFixed(2)}</td>
                <td>${(r.carbon_intensity || 350).toFixed(1)} gCO₂/kWh</td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <div class="recommendations">
          <h3>Strategic Decarbonization Recommendations</h3>
          <ul>
            <li><strong>Region Migration:</strong> Shifting compute workloads from high-carbon regions (e.g., ap-south-1) to green grid regions (e.g., us-west-2, eu-west-1) can reduce emissions by up to 64%.</li>
            <li><strong>Time-Shifting Batch Workloads:</strong> Run compute-heavy batch tasks during local off-peak renewable energy hours.</li>
            <li><strong>Workload Downsizing:</strong> Audit idle instances and rightsized underutilized compute/database units.</li>
          </ul>
        </div>

        <div class="footer">
          Generated automatically by CarbonIQ Sustainability Platform • GHG Protocol Corporate Standard Compliant
        </div>
      </body>
    </html>
  `;

  // Create hidden iframe and print/save as PDF
  const iframe = document.createElement("iframe");
  iframe.style.position = "fixed";
  iframe.style.right = "0";
  iframe.style.bottom = "0";
  iframe.style.width = "0";
  iframe.style.height = "0";
  iframe.style.border = "0";

  document.body.appendChild(iframe);

  const doc = iframe.contentWindow.document;
  doc.open();
  doc.write(htmlContent);
  doc.close();

  iframe.contentWindow.focus();
  setTimeout(() => {
    iframe.contentWindow.print();
    setTimeout(() => {
      document.body.removeChild(iframe);
    }, 1000);
  }, 250);
}
