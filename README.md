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

---

## API Keys

| Key | Where to get | Used for |
|-----|-------------|----------|
| `ELECTRICITY_MAPS_API_KEY` | [electricitymaps.com](https://electricitymaps.com) | Real carbon intensity per region/day |
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com/app/apikey) | AI insights & chatbot |
| `CLIMATIQ_API_KEY` | [climatiq.io](https://climatiq.io) | Appliance emission calculations |

---

## Multi-Agent Pipeline

When you upload a CUR CSV, 6 agents run in sequence:

1. **Ingestion** — parses CSV, skips Tax/Credit rows, compresses to daily buckets `(service, region, usage_type, day)`. 5600 rows → ~350 records.
2. **Region Mapping** — maps AWS regions to Electricity Maps zones (`ap-south-1` → `IN-WE`, etc.)
3. **Carbon Intensity** — fetches historical intensity per `(zone, day)` from Electricity Maps API. Past dates use `/carbon-intensity/past`, today uses `/latest`. Result is cached.
4. **Emission Calculation** — `emissions_kg = usage × power_factor × carbon_intensity / 1000`
5. **Analytics** — aggregates by service, region, and day for dashboard charts
6. **Optimization** — identifies region migration, time-shifting, and right-sizing opportunities

**API calls are minimal:** a CSV with 5000+ rows across 3 regions and 16 days = ~48 Electricity Maps API calls max (one per zone/day combo), all cached on re-upload.

---

## Supported AWS Services

EC2, Lambda, S3, RDS, SageMaker, EBS, ECS, EKS, DynamoDB, CloudFront, ElastiCache, CloudWatch, Glue, Amplify, EFS, API Gateway, DataZone, Cognito, SNS

---

## Project Structure

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
