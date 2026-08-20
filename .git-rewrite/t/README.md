# CarbonIQ — AWS Carbon Emissions Analyzer

Upload your AWS Cost & Usage Report (CUR) CSV and get instant carbon emissions insights powered by a 6-agent AI pipeline.

## Tech Stack

**Backend:** Python 3.12 · FastAPI 0.137 · httpx · Pydantic v2  
**Frontend:** React 19 · Vite 6 · Tailwind CSS · Recharts 3 · React Router 7

## Prerequisites

- Python 3.11+
- Node.js 18+

## Setup

### 1. Clone

```bash
git clone https://github.com/Atharvasp333/CarbonIQ.git
cd CarbonIQ
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

```env
CLIMATIQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
ELECTRICITY_MAPS_API_KEY=your_key_here
```

> All keys are optional — the app falls back to hardcoded emission factors if not provided.

Start the server:

```bash
python -m uvicorn main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

**First Time Setup:**
1. Create an account at `/signup`
2. Login at `/login`
3. Navigate to Dashboard (`/home`)
4. Connect AWS or load demo data

### Authentication
- Create account with any email/password
- Data stored in localStorage (demo mode)
- All routes protected except login/signup

### Routes
- `/` - Redirects to login or home
- `/login` - Login page
- `/signup` - Create account
- `/home` - Main dashboard (protected)
- `/reports` - Carbon reports with filters (protected)
- `/services` - AWS services overview (protected)
- `/service/:name` - Individual service details (protected)
- `/profile` - User profile (protected)
- `/settings` - App settings (protected)

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
CarbonIQ/
├── backend/
│   ├── main.py
│   ├── .env.example
│   ├── requirements.txt
│   ├── agents/
│   │   ├── ingestion_agent.py
│   │   ├── region_mapping_agent.py
│   │   ├── carbon_intensity_agent.py
│   │   ├── emission_calculation_agent.py
│   │   ├── analytics_agent.py
│   │   ├── optimization_agent.py
│   │   └── orchestrator.py
│   ├── routes/
│   │   ├── multi_agent_analysis.py
│   │   ├── service_analytics.py
│   │   └── ...
│   └── services/
│       ├── service_analyzer.py
│       ├── electricity_maps.py
│       ├── gemini.py
│       └── ...
└── frontend/
    ├── package.json
    └── src/
        └── components/
            ├── MultiAgentDashboard.jsx
            ├── ServiceDetailDashboard.jsx
            └── ...
```

---

## Notes

- **Do not commit your `.env` file** — it's gitignored.
- **Do not commit CUR CSV files** — they contain your AWS account ID. They're gitignored (`CUR_report*.csv`).
- The app works fully offline using fallback carbon intensity values if no API keys are set.
