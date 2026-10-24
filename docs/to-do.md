# CarbonIQ Master Task Tracker & Roadmap

This document maintains an accurate, up-to-date record of completed milestones, actively working components, and future feature backlogs.

---

## 🎯 Project Overview & Status

| Layer | Component | Status | Production Target |
|---|---|---|---|
| **Backend** | FastAPI + asyncpg + PostgreSQL | ✅ Production Ready | Render |
| **Frontend** | React 19 + Vite + Tailwind CSS | ✅ Production Ready | Vercel |
| **Database** | NeonDB (Serverless PostgreSQL) | ✅ Clean & Optimized | Neon.tech |
| **CLI & Tools** | Click + CodeCarbon + ElectricityMaps | ✅ Production Ready | Terminal / Scripts |
| **Python SDK** | `carboniq` Package | ✅ Built & Tested | Local / GitHub |
| **Sustainable Codegen** | AST Auditor & Code Refactorer | ✅ Built & Tested | Terminal / IDE |

---

## ✅ COMPLETED MILESTONES

### 1. Authentication & User Multi-Tenancy
- [x] Fixed password hashing using direct `bcrypt` implementation (Python 3.12+ compatible).
- [x] Multi-tenant user isolation on all routes (analyses, profile, recommendations, CLI measurements).
- [x] JWT verification with fallback support for Neon Auth and HS256 tokens.
- [x] Organization profile settings linked to user account.

### 2. Multi-Agent Cloud Carbon Accounting Engine
- [x] CUR Ingestion Agent (`csv_agent.py` and `compression_agent.py`) with gzip auto-decompression.
- [x] Region Mapping Agent (`region_mapping_agent.py`) mapping cloud zones to Electricity Maps grids.
- [x] Emission Calculation Agent (`emission_calculation_agent.py`) with power factors across EC2, S3, RDS, Lambda.
- [x] AWS S3 auto-sync discovery for new billing reports.

### 3. Sustainability Intelligence & Chatbot
- [x] Intelligence engine (`backend/routes/intelligence.py`) generating tailored green recommendations.
- [x] What-If Scenario Simulator for region migration and instance downsizing projections.
- [x] Google Gemini AI Chatbot with sustainability guardrails.

### 4. Carbon-Aware CLI & Monitoring
- [x] CodeCarbon hardware tracking (CPU, RAM, GPU energy in kWh & gCO2e).
- [x] `carboniq monitor` command for real-time terminal grid intensity monitoring.
- [x] `carboniq recommend-schedule` for green window region forecasting.
- [x] `carboniq compare` command for side-by-side benchmark comparison.
- [x] `carboniq stats` and `carboniq history` with cloud backend sync.

### 5. Developer Platform: API Keys & Web Dashboard Integration
- [x] Database migration: created `api_keys` and `workload_measurements` tables.
- [x] API key endpoints: `POST`, `GET`, `DELETE` at `/api/user/api-keys`.
- [x] Frontend page: **CLI & Workloads** tab added to dashboard with API key generation, active keys list, live KPI cards, and realtime measurement logs table.
- [x] CLI commands: `carboniq config set-key`, `carboniq config set-url`, and `carboniq whoami`.

### 6. Python Library & Sustainable Code Generation
- [x] Python package structure ([setup.py](file:///c:/Users/Admin/OneDrive/Documents/GitHub/CarbonIQ/setup.py) and `carboniq/`).
- [x] `@carboniq.track` decorator & context manager with automatic dashboard upload.
- [x] `@carboniq.defer_until_green` execution deferral based on grid intensity.
- [x] `carboniq audit <file.py>`: AST static code analyzer detecting energy anti-patterns and scoring code A-F.
- [x] `carboniq optimize <file.py>`: Automated green code refactoring (vectorization hints, `@lru_cache`, memory generators).
- [x] Full automated integration test suite ([tests/test_e2e_user_flow.py](file:///c:/Users/Admin/OneDrive/Documents/GitHub/CarbonIQ/tests/test_e2e_user_flow.py)) passing with 30/30 assertions (100% success).

---

## ⏳ ACTIVE & REMAINING ROADMAP (Next Steps)

### High Priority
1. **PyPI Distribution (`pip install carboniq`)**:
   - Register package name on PyPI.
   - Build source distribution (`python -m build`) and upload using Twine.
2. **VS Code / Cursor / IDE Plugin**:
   - Create a lightweight VS Code extension that executes `carboniq audit` on file save to highlight high-carbon lines with green quick-fixes.

### Medium Priority
3. **Downloadable Executive PDF Reports**:
   - Add PDF export for sustainability compliance and stakeholder reporting.
4. **Physical Feasibility Warnings in What-If Simulator**:
   - Flag migration complexity warnings for regional managed services (e.g., DynamoDB, API Gateway).

### Low Priority / Future Enhancements
5. **Multi-Cloud CUR Ingestion**: Support GCP BigQuery export and Azure Cost Management exports.
6. **Carbon Budgets & Webhook Alerts**: Configurable monthly gCO2e budget caps with Slack/email alerts.