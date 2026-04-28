# CarbonIQ Cloud Analyzer

A full-stack web dashboard that converts AWS billing CSV data into carbon emissions insights and visual analytics. Upload your AWS Cost and Usage Report and get instant carbon intelligence with AI-powered optimization recommendations.

## 🌟 Features

### Core Functionality
- 📊 **CSV Upload**: Accept AWS billing CSV with automatic parsing
- 🌍 **Carbon Conversion**: Convert AWS usage into CO₂ emissions using region-specific factors
- 📈 **Visual Analytics**: Interactive charts and graphs
- 🤖 **AI Insights**: Google Gemini-powered optimization recommendations
- 🔮 **What-If Simulator**: Test different optimization scenarios
- ⚠️ **Idle Resource Detection**: Identify wasteful spending
- 💰 **Cost vs Emissions**: Understand the relationship between spend and carbon

### Dashboard Components
- **Top Metrics Cards**: Total CO₂, Cost, Top Region, Top Service
- **Pie Chart**: Emissions by Service (EC2, RDS, Lambda, S3, etc.)
- **Bar Charts**: Emissions by Region and Instance Type
- **Scatter Plot**: Cost vs CO₂ correlation
- **Data Table**: Detailed line items with service, region, usage, cost, CO₂
- **AI Insights Panel**: Actionable recommendations with priority levels
- **What-If Simulator**: Scenario planning for optimization

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- AWS billing CSV (or use included demo data)

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Edit `backend/.env` and add your API keys (optional):
```
CLIMATIQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

Start the backend:
```bash
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## 📊 AWS CSV Format

The app expects AWS Cost and Usage Report CSV with these headers:

```
identity/LineItemId
bill/BillingPeriodStartDate
lineItem/UsageStartDate
lineItem/UsageEndDate
product/ProductName
product/region
lineItem/UsageType
lineItem/UsageAmount
product/instanceType
lineItem/ResourceId
lineItem/UnblendedCost
```

## 🧮 Carbon Calculation

### Region Emission Factors (kg CO₂/kWh)
- us-west-1 (California): 0.285 - Low carbon
- us-west-2 (Oregon): 0.285 - Low carbon
- eu-west-1 (Ireland): 0.295 - Low carbon
- us-east-1 (Virginia): 0.415 - Medium carbon
- ap-northeast-1 (Tokyo): 0.463 - Medium carbon
- ap-south-1 (Mumbai): 0.708 - High carbon
- us-east-2 (Ohio): 0.744 - High carbon

### Formula
```
CO₂ (kg) = UsageAmount × ServicePowerFactor × RegionEmissionFactor
```

## 🤖 AI Features

### Gemini-Powered Insights
- Region optimization recommendations
- Instance right-sizing suggestions
- Idle resource identification
- Carbon budget tracking
- Cost-saving opportunities

### Chatbot Assistant
- Ask questions about AWS carbon footprint
- Get sustainability best practices
- Learn about emission reduction strategies
- Understand cloud optimization

## 🎯 Demo Data

The app includes realistic mock data showing:
- ~450 kg CO₂ total emissions
- Multiple AWS services (EC2, RDS, Lambda, S3, EBS)
- Various regions (us-east-1, us-west-2, eu-west-1, ap-south-1)
- Different instance types (m5.large, t3.medium, etc.)
- Idle resource examples

## 🛠️ Tech Stack

**Backend**
- FastAPI (Python)
- Pydantic for data validation
- Google Gemini API for AI insights
- Climatiq API for emission factors (optional)

**Frontend**
- React 18 + Vite
- Tailwind CSS for styling
- Recharts for data visualization
- Axios for API calls

## 📁 Project Structure

```
carboniq/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── routes/
│   │   ├── emissions.py        # CSV upload & analysis
│   │   ├── insights.py         # AI recommendations
│   │   ├── whatif.py           # Scenario simulator
│   │   └── chat.py             # Chatbot endpoint
│   ├── services/
│   │   ├── aws_analyzer.py     # CSV parser & calculator
│   │   ├── gemini.py           # AI integration
│   │   └── climatiq.py         # Emission factors
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   └── data/
│       └── mock_csv.csv        # Demo data
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── UploadSection.jsx
│   │   │   ├── MetricsBar.jsx
│   │   │   ├── EmissionsPieChart.jsx
│   │   │   ├── TrendChart.jsx
│   │   │   ├── DataTable.jsx
│   │   │   ├── AIInsightsPanel.jsx
│   │   │   ├── WhatIfSimulator.jsx
│   │   │   └── ChatBot/
│   │   ├── api/
│   │   │   └── client.js
│   │   └── App.jsx
│   └── package.json
└── README.md
```

## 🔑 API Keys

### Gemini API (Free)
1. Visit https://aistudio.google.com/app/apikey
2. Create a new API key
3. Add to `backend/.env`

### Climatiq API (Optional)
1. Visit https://climatiq.io
2. Sign up for free tier
3. Add to `backend/.env`

**Note**: The app works without API keys using fallback calculations and suggestions.

## 🌐 API Endpoints

- `GET /api/health` - Health check
- `POST /api/upload-csv` - Upload AWS billing CSV
- `GET /api/mock-data` - Load demo data
- `POST /api/insights` - Get AI recommendations
- `POST /api/whatif` - Run scenario simulation
- `POST /api/chat` - Chat with AI assistant

## 💡 Usage Tips

1. **Start with Demo Data**: Click "Load Demo Data" to see the dashboard in action
2. **Upload Your CSV**: Export AWS Cost and Usage Report and upload
3. **Review Insights**: Check the AI Insights tab for optimization recommendations
4. **Test Scenarios**: Use What-If simulator to plan changes
5. **Ask Questions**: Use the chatbot for specific sustainability questions

## 🎨 Key Insights Provided

- **Region Optimization**: Move workloads to low-carbon regions (30-40% reduction)
- **Idle Resources**: Identify and remove unused resources (15-20% savings)
- **Instance Right-Sizing**: Downsize over-provisioned instances (25% reduction)
- **Service Optimization**: Optimize storage and serverless configurations (10% savings)

## 📈 Carbon Budget

The app calculates:
- Current monthly emissions
- Recommended target (30% reduction)
- Budget status (over_budget / on_track / excellent)
- Progress visualization

## 🤝 Contributing

This is a demo application. Feel free to fork and customize for your needs.

## 📄 License

MIT

## 🙏 Acknowledgments

- AWS for cloud infrastructure
- Google Gemini for AI capabilities
- Climatiq for emission factor data
- Recharts for visualization components

---

**Built with ❤️ for a sustainable cloud future**
