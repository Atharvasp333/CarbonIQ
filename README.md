# CarbonIQ — AWS Carbon Emissions Analyzer + CLI Tool

Upload your AWS Cost & Usage Report (CUR) or connect your S3 bucket directly — CarbonIQ runs it through a 6-agent AI pipeline to calculate carbon emissions, identify optimization opportunities, and deliver actionable sustainability insights.

**NEW:** Carbon-Aware CLI tool for real-time workload measurement with CodeCarbon + Electricity Maps API integration.

## What It Does

### Web Dashboard
1. User signs up / logs in (Neon Auth — real JWT sessions, no localStorage mock)
2. Connects their AWS account once (credentials saved per-user in NeonDB)
3. CUR CSVs are auto-fetched from their S3 bucket on every session, or manually uploaded
4. A 6-agent pipeline processes the data: ingestion → region mapping → carbon intensity → emission calculation → analytics → optimization
5. Dashboard shows emissions by service, region, and time — with AI-powered recommendations

### Python SDK & CLI Tool
1. **Package Installation**: Install globally via `pip install -e .`
2. **Personalized Authentication**: Connect terminal runs to your account using API Keys (`carboniq config set-key ciq_live_...`)
3. **Function Tracking Decorators**: Wrap functions with `@carboniq.track` to measure hardware CPU/RAM kWh & emissions
4. **Sustainable Code Engine**: Run `carboniq audit` and `carboniq optimize` to eliminate energy anti-patterns and generate green Python code
5. **Real-Time Grid Monitoring**: Live carbon intensity tracking (`carboniq monitor`) and off-peak scheduling recommendations (`carboniq recommend-schedule`)

---

## Tech Stack

| Layer | Stack |
|---|---|
| Backend | Python 3.12+ · FastAPI · asyncpg · Pydantic v2 · bcrypt |
| Database | NeonDB (PostgreSQL) via asyncpg connection pooling |
| Auth | Multi-tenant JWT sessions + SHA-256 API Key authorization |
| Python SDK | `carboniq` (CodeCarbon + AST Analyzer + Grid Client) |
| CLI Tool | Click 8 · CodeCarbon · Requests |
| AI / ML | Google Gemini 2.5-flash · AST Sustainable Codegen Engine · 6-Agent accounting pipeline |
| Carbon Data | Electricity Maps API · Climatiq API |
| AWS | boto3 · S3 CUR fetching (csv + csv.gz) |
| Frontend | React 19 · Vite 6 · Tailwind CSS · Recharts · React Router 7 |

---

## Project Structure

```
CarbonIQ/
├── backend/
│   ├── main.py                  # FastAPI app with registered routers
│   ├── database.py              # NeonDB pool, table init, migrations
│   ├── routes/
│   │   ├── auth.py              # Auth routes (signup, login, me)
│   │   ├── api_keys.py          # API key generation & validation
│   │   ├── cli_measurements.py  # User-specific CLI measurement ingestion & stats
│   │   ├── intelligence.py      # Recommendations & AI insights
│   │   ├── aws_integration.py   # S3 CUR fetching
│   │   └── ...
│   └── agents/                  # Multi-agent accounting engine
├── carboniq/                    # 📦 Python SDK & Sustainable Codegen Engine
│   ├── __init__.py              # Exports track, defer_until_green, audit_code, optimize_code
│   ├── tracker.py               # CodeCarbon decorator & context manager
│   ├── grid.py                  # Carbon-aware execution & intensity checks
│   └── optimizer.py             # AST static carbon auditor & code refactorer
├── cli/                         # 🖥️ CarbonIQ CLI Tool
│   ├── carboniq_cli.py          # Click CLI entry point
│   ├── config_manager.py        # Persistent ~/.carboniq/config.json manager
│   ├── backend_client.py        # Authenticated backend client
│   └── carbon_aware.py          # Electricity Maps API client
├── frontend/
│   └── src/
│       ├── pages/main/
│       │   ├── CLIWorkloads.jsx # 🆕 API Keys & Realtime Measurement Logs
│       │   ├── Home.jsx         # Upload + AWS connect dashboard
│       │   ├── Insights.jsx     # AI recommendations & What-If simulator
│       │   └── ...
├── tests/
│   └── test_e2e_user_flow.py    # 🧪 Automated E2E integration test suite (30/30 tests)
├── setup.py                     # Python package installer (pip install -e .)
├── .env                         # Unified environment configuration
└── README.md
```

---

## Setup

### 1. Clone

```bash
git clone https://github.com/Atharvasp333/CarbonIQ.git
cd CarbonIQ
```

### 2. Environment Configuration (Single .env file)

Copy the example and fill in your credentials:

```bash
cp .env.example .env
```

Fill in `.env` (root directory - works for both backend and CLI):

```env
# Backend Database & Auth
DATABASE_URL=your_neon_postgres_connection_string
JWT_SECRET=a_long_random_string
NEON_AUTH_URL=https://<your-project>.neonauth.<region>.aws.neon.tech/<dbname>/auth
CREDS_ENCRYPTION_KEY=generate_with_fernet

# External APIs
CLIMATIQ_API_KEY=your_key          # optional
GEMINI_API_KEY=your_key            # optional
ELECTRICITY_MAPS_API_KEY=your_key  # required for CLI carbon-aware features

# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
AWS_BUCKET_NAME=your-bucket-name
AWS_FILE_PREFIX=path/to/cur/files/

# CLI Configuration
CARBONIQ_API_URL=http://localhost:8000/api
CODECARBON_TRACKING_MODE=machine
CODECARBON_OUTPUT_DIR=./cli/measurements
CODECARBON_LOG_LEVEL=info
```

### 3. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt
cd ..

# Frontend
cd frontend
npm install
cd ..
```

### 4. Start Everything (Single Command!)

**Windows (PowerShell):**
```powershell
.\start-dev.ps1
```

**Linux/Mac:**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

This starts both backend and frontend in one command!
- 🌐 Frontend: http://localhost:5173
- ⚡ Backend: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

Press `Ctrl+C` to stop all services.

**Or manually (separate terminals):**
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Frontend  
cd frontend
npm run dev
```

### 5. CLI Tool (Optional - for Carbon-Aware Workload Measurement)

```bash
cd cli
pip install -r requirements.txt

# Test Electricity Maps integration
python carboniq_cli.py test-electricity-maps

# Measure a Python workload
python carboniq_cli.py measure python sample_workloads/simple_task.py

# Measure with carbon-aware recommendations
python carboniq_cli.py measure python sample_workloads/compute_intensive.py --check-carbon-intensity
```

---

## Authentication

- Powered by **Neon Auth** (Better Auth under the hood)
- Sign up / login with email + password
- Sessions are JWT-based — no localStorage credential storage
- All `/home`, `/reports`, `/services`, `/profile`, `/settings` routes are protected
- `NeonAuthUIProvider` wraps the app — pre-built sign-in / sign-up UI available via `AuthView`

---

## AWS Auto-Sync Flow

1. First login → dashboard shows an **"Connect AWS"** banner
2. User enters: Access Key, Secret Key, Region, S3 Bucket name
3. Credentials are validated against S3 and saved to NeonDB (encrypted at rest by Neon)
4. On subsequent logins, CarbonIQ auto-fetches the latest CUR CSV from S3 and runs the pipeline
5. User can still manually upload a CSV anytime
6. Credentials can be updated or removed from the dashboard

> IAM permissions needed: `s3:GetObject`, `s3:ListBucket` on the CUR bucket.

---

## 6-Agent Pipeline

```
CSV (uploaded or S3 auto-fetch)
  │
  ▼
Agent 1 — Ingestion & Normalization
  Parse, validate, skip Tax/Credit rows
  Compress 5,000+ rows → ~200 daily records by (service, region, day)
  │
  ▼
Agent 2 — Region Mapping
  Map AWS regions to Electricity Maps zones
  e.g. ap-south-1 → IN-WE, us-west-2 → US-NW-PACW
  │
  ▼
Agent 3 — Carbon Intensity
  Fetch historical gCO₂/kWh from Electricity Maps API
  Deduplicated cache by (zone, day) — ~48 API calls for 16-day report
  Fallback: hardcoded regional averages if API unavailable
  │
  ▼
Agent 4 — Emission Calculation
  CO₂ (kg) = UsageAmount × ServicePowerFactor × CarbonIntensity / 1000
  Service factors: EC2 0.15 kWh/hr, Lambda 0.0001 kWh/GB-s, S3 0.0005 kWh/GB
  │
  ▼
Agent 5 — Analytics
  Aggregate by service, region, time
  Generate time-series hourly data
  Identify highest emitter and idle resources
  │
  ▼
Agent 6 — Optimization
  Region migration suggestions (e.g. ap-south-1 708→us-west-2 220 gCO₂/kWh = 69% reduction)
  Time-shifting recommendations (off-peak hours)
  Idle resource cleanup
  Ranked by impact + feasibility
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/signup` | Create account |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Validate session |
| POST | `/api/aws/credentials` | Save user's S3 credentials |
| GET | `/api/aws/credentials` | Get saved credentials (keys masked) |
| DELETE | `/api/aws/credentials` | Remove saved credentials |
| POST | `/api/aws/fetch` | Fetch CUR CSV from S3 |
| POST | `/api/aws/auto-sync` | Auto-fetch latest CUR using saved credentials |
| POST | `/api/multi-agent/analyze` | Run 6-agent pipeline on uploaded CSV |
| POST | `/api/multi-agent/analyze-demo` | Run pipeline on demo data |
| POST | `/api/service-analytics/store` | Persist analysis results |
| GET | `/api/service-analytics/summary` | Get aggregated service breakdown |
| GET | `/api/service-analytics/service/:name` | Service drill-down |
| POST | `/api/insights` | Get Gemini AI recommendations |
| POST | `/api/whatif` | What-if scenario simulation |
| POST | `/api/chat` | ChatBot Q&A |
| GET | `/api/health` | Health check (API key status + DB) |

---

## Frontend Routes

| Path | Description |
|---|---|
| `/` | Redirect → `/login` or `/home` |
| `/login` | Neon Auth login |
| `/signup` | Neon Auth signup |
| `/home` | Dashboard — upload CSV or connect AWS |
| `/reports` | Charts, trends, time-series analysis |
| `/services` | AWS service emissions grid |
| `/service/:name` | Service drill-down with regional breakdown |
| `/profile` | User profile |
| `/settings` | App settings |

---

## Database Schema (NeonDB)

- `users` — id, name, email, password (bcrypt), created_at
- `aws_credentials` — user_id, access_key, secret_key, region, bucket_name, verified_at
- `analyses` — id, filename, timestamps, summary metrics
- `emission_records` — per-record emissions data linked to analysis
- `api_call_logs` — Electricity Maps API call history

---

---

## Complete End-to-End User Journey

### Scenario: Student Analyzes AWS Billing + Measures Local Workloads

#### Step 1: Initial Setup (One-time)
```bash
# Clone repository
git clone https://github.com/Atharvasp333/CarbonIQ.git
cd CarbonIQ

# Configure environment
cp .env.example .env
# Edit .env with your API keys and AWS credentials

# Start backend
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000

# In new terminal: Start frontend
cd frontend
npm install
npm run dev

# In new terminal: Setup CLI
cd cli
pip install -r requirements.txt
```

#### Step 2: Web Dashboard - Analyze AWS Billing
```
1. Open browser to http://localhost:5173
2. Sign up with email/password
3. Login → lands on Dashboard
4. Click "Connect AWS Account"
5. Enter:
   - Access Key: AKIA5IODSONOQSZMMT3M
   - Secret Key: (from .env)
   - Region: us-east-1
   - Bucket: carboniq-bucket
   - File Prefix: carboniq-cur/carboniq-cur/data/
6. Click "Validate & Save"

Backend auto-fetches latest CUR CSV from S3 → runs 6-agent pipeline → results appear:

**Dashboard Shows:**
- Total Emissions: 5.66 kg CO2e
- Total Cost: $42.87
- Top Service: AWS Glue (5.30 kg CO2e)
- Top Region: ap-south-1 (708 gCO2/kWh)

**Recommendations Panel:**
✅ Migrate AWS Glue from ap-south-1 to eu-west-1 → 73% emissions reduction
✅ Time-shift batch processing to 2-6 AM UTC → 35% cleaner grid
✅ Cleanup idle Lambda functions → $3.20/month savings

7. Navigate to "/reports" → See time-series charts
8. Navigate to "/services" → Drill down into AWS Glue regional breakdown
```

#### Step 3: CLI - Measure Local Python Workload
```powershell
cd cli

# Check current carbon intensity across regions
python carboniq_cli.py test-electricity-maps

Output:
🌍 Carbon Intensity by Region:
   US-East-1 (Virginia):     394 gCO2/kWh
   US-West-2 (Oregon):       220 gCO2/kWh  ✅ BEST
   EU-West-1 (Ireland):      105 gCO2/kWh  ✅ BEST
   AP-South-1 (Mumbai):      708 gCO2/kWh  ⚠️ HIGH

# Measure a compute-intensive workload
python carboniq_cli.py measure python sample_workloads/compute_intensive.py --check-carbon-intensity

Output:
⏱️  Measurement started...
🔍 Checking carbon intensity...
🌍 Optimal region: EU-West-1 (105 gCO2/kWh)
⚠️  Current region: US-East-1 (394 gCO2/kWh)
💡 Running here produces 73% more emissions than optimal region

[workload runs...]

✅ Measurement complete!
📊 Results:
   Duration: 42.3 seconds
   Energy: 0.0234 kWh
   Emissions: 9.22 gCO2e
   Location: US-East-1
   If run in EU-West-1: 2.49 gCO2e (73% savings!)

📁 Results saved to: cli/measurements/Compute_Intensive_Test_20261024_153015.json
```

#### Step 4: Real-Time Sync with CarbonIQ Dashboard
Workload measurements automatically stream to the user's dashboard over authenticated HTTPS:
```bash
# Set your API Key once
carboniq config set-key ciq_live_your_key_here

# Measure any workload — automatically posted to your user dashboard
carboniq measure -n "AI-Model-Training" -t "ml-training" -- python train.py
```

#### Step 5: Unified Cloud & Local Emissions Intelligence
The CarbonIQ web dashboard aggregates both data streams:
- **Cloud Footprint (AWS CUR)**: Macro-level infrastructure emissions, scope accounting, and region-shift recommendations.
- **Local & CI/CD Compute (CLI Workloads)**: Micro-level execution measurements (CPU/RAM kWh, gCO2e) synced in real time.
- **Sustainability Governance**: Track total carbon emissions across development lifecycles in one unified platform.

### Key Insights from This Journey

**From AWS Billing Analysis:**
- Real AWS usage (Oct 2026): 5.66 kg CO2e
- Largest emitter: AWS Glue in high-carbon region (ap-south-1)
- 73% potential savings by regional migration

**From CLI Tool:**
- Real-time carbon intensity awareness before running workloads
- Actual measurement using CodeCarbon (not estimates)
- Carbon-aware scheduling recommendations

**Combined Impact:**
- Student can track both cloud (AWS) and local (laptop) carbon footprint
- Data-driven decisions on where and when to run workloads
- Demonstrable emissions reduction for capstone presentation

---

## Project Status & Roadmap

### Completed Milestones
- [x] Multi-agent AWS Cost and Usage Report (CUR) carbon accounting engine with gzip streaming decompression.
- [x] Multi-tenant database architecture with NeonDB (PostgreSQL) and user isolation across analyses and organization profiles.
- [x] Full developer authentication platform with JWT sessions and SHA-256 API key issuance (`ciq_live_...`).
- [x] Real-time workload emission telemetry ingestion and analytics pipeline.
- [x] Explainable AI sustainability recommendation engine with organizational constraint validation.
- [x] Sustainable AST Code Optimizer & green refactoring generator (`carboniq audit` and `carboniq optimize`).
- [x] End-to-end integration and user lifecycle validation suite (30/30 tests passing).

### Active Roadmap & Planned Enhancements
- [ ] PyPI distribution for global installation (`pip install carboniq`).
- [ ] VS Code / IDE Marketplace Extension for inline green code recommendations and audit warnings.
- [ ] Downloadable executive sustainability compliance reports (PDF export).
- [ ] Extended emission calculation factors for Amazon API Gateway and managed messaging services.
- [ ] Multi-cloud billing report ingestion for Google Cloud Platform (GCP) and Microsoft Azure.
