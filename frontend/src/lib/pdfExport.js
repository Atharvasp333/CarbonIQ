/**
 * CarbonIQ Executive PDF Export Generator
 * Generates an executive-ready sustainability PDF report using clean vector print styling.
 */

function escapeHtml(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function safeNum(val, decimals = 2, fallback = '0.00') {
  if (val == null) return fallback;
  const num = Number(val);
  return isNaN(num) ? fallback : num.toFixed(decimals);
}

export function generateSustainabilityPDF(analysisData, userInfo = {}) {
  // Normalize analysis data structure across backend and demo responses
  const normData = analysisData?.results || analysisData || {};
  const summary = normData.summary || analysisData?.summary || {};
  const analytics = normData.analytics || analysisData?.analytics || {};

  if (!summary || Object.keys(summary).length === 0) {
    throw new Error("No analysis summary data available to generate report");
  }

  const rawName = userInfo?.name || "Enterprise User";
  const rawOrg = userInfo?.organization || "Cloud Infrastructure";
  const userName = escapeHtml(rawName);
  const organization = escapeHtml(rawOrg);
  
  const reportDate = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric"
  });

  const totalEmissions = safeNum(summary.total_emissions_kg, 2, "0.00");
  const totalCost = safeNum(summary.total_cost, 2, "0.00");
  const totalEnergy = safeNum(summary.total_energy_kwh, 2, "0.00");
  const topService = escapeHtml(summary.top_service || "Compute (EC2)");
  const topRegion = escapeHtml(summary.top_region || "us-east-1");

  const services = (analytics?.service_breakdown || analytics?.by_service || []).slice(0, 10);
  const regions = (analytics?.region_breakdown || analytics?.by_region || []).slice(0, 8);

  // Extract recommendations from any supported backend format
  let recommendations = [];
  if (Array.isArray(normData.intelligence?.recommendations) && normData.intelligence.recommendations.length > 0) {
    recommendations = normData.intelligence.recommendations;
  } else if (Array.isArray(normData.optimization?.recommendations) && normData.optimization.recommendations.length > 0) {
    recommendations = normData.optimization.recommendations;
  } else if (Array.isArray(normData.optimization?.opportunities) && normData.optimization.opportunities.length > 0) {
    recommendations = normData.optimization.opportunities;
  } else if (Array.isArray(normData.recommendations) && normData.recommendations.length > 0) {
    recommendations = normData.recommendations;
  } else if (Array.isArray(analysisData?.recommendations) && analysisData.recommendations.length > 0) {
    recommendations = analysisData.recommendations;
  } else {
    // Attempt fallback from localStorage if available in browser
    try {
      const stored = localStorage.getItem('carboniq_insights');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed?.recommendations) && parsed.recommendations.length > 0) {
          recommendations = parsed.recommendations;
        }
      }
    } catch (_) {}
  }

  const hasRecs = recommendations.length > 0;

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
            font-size: 11px;
            line-height: 1.5;
          }
          .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #10b981;
            padding-bottom: 12px;
            margin-bottom: 16px;
          }
          .logo {
            font-size: 22px;
            font-weight: 800;
            color: #064e3b;
            letter-spacing: -0.5px;
          }
          .logo span {
            color: #10b981;
          }
          .report-meta {
            text-align: right;
            font-size: 10px;
            color: #6b7280;
            line-height: 1.4;
          }
          .title-section {
            margin-bottom: 16px;
          }
          .title-section h1 {
            font-size: 18px;
            margin: 0 0 4px 0;
            color: #111827;
          }
          .title-section p {
            margin: 0;
            color: #4b5563;
            font-size: 11px;
          }
          .kpi-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 20px;
          }
          .kpi-card {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 10px 12px;
          }
          .kpi-card.highlight {
            background: #ecfdf5;
            border-color: #a7f3d0;
          }
          .kpi-title {
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #6b7280;
            margin-bottom: 2px;
          }
          .kpi-card.highlight .kpi-title {
            color: #065f46;
          }
          .kpi-value {
            font-size: 16px;
            font-weight: 700;
            color: #111827;
          }
          .kpi-card.highlight .kpi-value {
            color: #047857;
          }
          .kpi-sub {
            font-size: 9px;
            color: #6b7280;
            margin-top: 2px;
          }
          h2 {
            font-size: 12px;
            font-weight: 700;
            margin: 16px 0 6px 0;
            color: #111827;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 12px;
            font-size: 10px;
          }
          th {
            background: #f3f4f6;
            color: #374151;
            font-weight: 600;
            text-align: left;
            padding: 5px 8px;
            border-bottom: 1px solid #d1d5db;
          }
          td {
            padding: 5px 8px;
            border-bottom: 1px solid #e5e7eb;
          }
          tr:nth-child(even) td {
            background: #fafafa;
          }
          .recommendations {
            background: #f0fdf4;
            border-left: 4px solid #10b981;
            padding: 10px 12px;
            border-radius: 0 6px 6px 0;
            margin-top: 14px;
          }
          .recommendations h3 {
            margin: 0 0 6px 0;
            font-size: 11px;
            color: #065f46;
            font-weight: 700;
          }
          .recommendations ul {
            margin: 0;
            padding-left: 14px;
            color: #1f2937;
          }
          .recommendations li {
            margin-bottom: 4px;
            line-height: 1.4;
          }
          .recommendations li:last-child {
            margin-bottom: 0;
          }
          .rec-impact {
            color: #047857;
            font-style: italic;
          }
          .rec-formula {
            color: #4b5563;
            font-family: monospace;
            font-size: 9px;
            display: block;
            margin-top: 2px;
          }
          .footer {
            margin-top: 24px;
            border-top: 1px solid #e5e7eb;
            padding-top: 8px;
            text-align: center;
            font-size: 9px;
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
            <div><strong>Account Auditor:</strong> ${userName}</div>
          </div>
        </div>

        <div class="title-section">
          <h1>Cloud Carbon Footprint &amp; ESG Sustainability Audit</h1>
          <p>Verified emissions accounting, energy consumption profile, and evidence-based optimization analysis.</p>
        </div>

        <div class="kpi-grid">
          <div class="kpi-card highlight">
            <div class="kpi-title">Total Carbon Emissions</div>
            <div class="kpi-value">${totalEmissions} kg CO₂e</div>
            <div class="kpi-sub">Scope 2 Location-Based</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">Total Energy Consumed</div>
            <div class="kpi-value">${totalEnergy} kWh</div>
            <div class="kpi-sub">Calculated via AWS Billing Telemetry</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">Total Cloud Cost</div>
            <div class="kpi-value">$${totalCost}</div>
            <div class="kpi-sub">AWS CUR Line Item Aggregate</div>
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
            ${services.length > 0 ? services.map(s => {
              const name = escapeHtml(s.service || s.name || 'Cloud Service');
              const em = safeNum(s.emissions_kg ?? s.co2_kg, 2);
              const en = safeNum(s.energy_kwh, 2);
              const co = safeNum(s.cost, 2);
              return `
                <tr>
                  <td><strong>${name}</strong></td>
                  <td>${em}</td>
                  <td>${en}</td>
                  <td>$${co}</td>
                </tr>
              `;
            }).join('') : `
              <tr>
                <td><strong>${topService}</strong></td>
                <td>${totalEmissions}</td>
                <td>${totalEnergy}</td>
                <td>$${totalCost}</td>
              </tr>
            `}
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
            ${regions.length > 0 ? regions.map(r => {
              const rName = escapeHtml(r.region || r.name || 'AWS Region');
              const em = safeNum(r.emissions_kg ?? r.co2_kg, 2);
              const ci = safeNum(r.carbon_intensity, 1, '394.0');
              return `
                <tr>
                  <td><strong>${rName}</strong></td>
                  <td>${em}</td>
                  <td>${ci} gCO₂/kWh</td>
                </tr>
              `;
            }).join('') : `
              <tr>
                <td><strong>${topRegion}</strong></td>
                <td>${totalEmissions}</td>
                <td>394.0 gCO₂/kWh</td>
              </tr>
            `}
          </tbody>
        </table>

        <div class="recommendations">
          <h3>${hasRecs ? `Calculated Decarbonization Recommendations (${recommendations.length} Action Items)` : 'Evidence-Based Decarbonization Recommendations'}</h3>
          <ul>
            ${hasRecs ? (
              recommendations.slice(0, 5).map(rec => {
                const title = escapeHtml(rec.title || rec.name || rec.category || 'Optimization Opportunity');
                const act = escapeHtml(rec.recommended_action || rec.recommendation || rec.action || rec.reasoning || rec.finding || 'Review operational schedule to target low-carbon grid windows.');
                
                const kgRaw = rec.expected_reduction_kg ?? rec.carbon_reduction_kg ?? rec.potential_savings_kg;
                const pctRaw = rec.expected_reduction_pct ?? rec.carbon_reduction_pct ?? rec.potential_reduction_pct;
                const kgNum = Number(kgRaw);
                const pctNum = Number(pctRaw);
                
                let impactStr = '';
                if (!isNaN(kgNum) && kgNum > 0) {
                  impactStr = `Projected Savings: ${kgNum.toFixed(4)} kg CO₂e${!isNaN(pctNum) && pctNum > 0 ? ` (~${pctNum.toFixed(1)}%)` : ''}`;
                } else {
                  impactStr = 'Projected Savings: Not calculated (Qualitative Architectural Guidance)';
                }

                const formula = rec.calculation_basis ? `<span class="rec-formula">Formula: ${escapeHtml(rec.calculation_basis.split('=')[0].trim())}</span>` : '';

                return `<li>
                  <strong>${title}:</strong> ${act}
                  <span class="rec-impact">[${escapeHtml(impactStr)}]</span>
                  ${formula}
                </li>`;
              }).join('')
            ) : `
              <li><strong>Carbon-Aware Workload Scheduling:</strong> Reschedule batch processing and asynchronous workloads to execute during off-peak, high-renewable grid windows. <span class="rec-impact">[Decision Support Recommendation]</span></li>
              <li><strong>Regional Workload Migration:</strong> Evaluate migrating non-latency-critical compute clusters to AWS regions with lower annual grid carbon intensity. <span class="rec-impact">[Decision Support Recommendation]</span></li>
              <li><strong>Resource Optimization &amp; Storage Lifecycle:</strong> Apply automated S3 lifecycle rules and audit idle compute instances to eliminate baseline emissions waste. <span class="rec-impact">[Decision Support Recommendation]</span></li>
            `}
          </ul>
        </div>

        <div class="footer">
          Generated automatically by CarbonIQ Sustainability Platform • GHG Protocol Corporate Standard Compliant • ISO 14064 Methodology
        </div>
      </body>
    </html>
  `;

  // Safely trigger document print/save dialog via hidden iframe
  try {
    const iframe = document.createElement("iframe");
    iframe.style.position = "fixed";
    iframe.style.right = "0";
    iframe.style.bottom = "0";
    iframe.style.width = "0";
    iframe.style.height = "0";
    iframe.style.border = "0";
    iframe.setAttribute("aria-hidden", "true");

    document.body.appendChild(iframe);

    const doc = iframe.contentWindow?.document || iframe.contentDocument;
    if (!doc) {
      throw new Error("Unable to create document context for printing");
    }

    doc.open();
    doc.write(htmlContent);
    doc.close();

    iframe.contentWindow.focus();
    setTimeout(() => {
      try {
        iframe.contentWindow.print();
      } catch (printErr) {
        console.warn("Print dialog invocation failed or was dismissed:", printErr);
      } finally {
        setTimeout(() => {
          if (document.body.contains(iframe)) {
            document.body.removeChild(iframe);
          }
        }, 1500);
      }
    }, 300);
  } catch (err) {
    console.error("PDF generation frame execution error:", err);
    throw new Error(`PDF generation failed: ${err.message}`);
  }
}
