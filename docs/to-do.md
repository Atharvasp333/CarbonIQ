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

### 1. Authentication & Multi-Tenant User Isolation
- [x] Implemented secure password hashing via `bcrypt` (Python 3.12+ compatible).
- [x] Multi-tenant data isolation across all domains (`analyses`, `organization_profile`, `recommendations`, `workload_measurements`).
- [x] Hybrid JWT verification supporting Neon Auth Ed25519 (EdDSA via JWKS) and legacy HS256 tokens.
- [x] Organization profile schema and questionnaire integration linked strictly to authenticated user identity.
- [x] Direct user association in `analyses` table via foreign key `user_id` and automatic schema migration.

### 2. Multi-Agent Cloud Carbon Accounting Engine
- [x] CUR Ingestion Agent (`csv_agent.py` & `compression_agent.py`) with memory-efficient streaming gzip decompression.
- [x] Regional Mapping Agent (`region_mapping_agent.py`) correlating cloud zones with Electricity Maps bidding zones.
- [x] Emission Calculation Agent (`emission_calculation_agent.py`) utilizing power factors for EC2, S3, RDS, and Lambda.
- [x] AWS S3 integration with automated credential encryption and billing report discovery.

### 3. Explainable Sustainability Intelligence
- [x] Multi-stage recommendation orchestrator delivering domain-specific decarbonization strategies.
- [x] Interactive What-If Scenario Simulator for regional migration and instance downsizing projections.
- [x] Contextual conversational AI assistant with sustainability domain guardrails.

### 4. Carbon-Aware Workload Telemetry & CLI
- [x] Physical hardware telemetry via CodeCarbon (CPU, RAM, GPU energy in kWh & emissions in gCO2e).
- [x] Real-time terminal grid intensity monitoring (`carboniq monitor`).
- [x] Forecasting engine for carbon-optimal execution windows (`carboniq recommend-schedule`).
- [x] Differential benchmarking utility (`carboniq compare`).
- [x] Live cloud sync for workload execution metrics (`carboniq stats` and `carboniq history`).

### 5. Developer Platform & API Key Infrastructure
- [x] NeonDB schema migrations for `api_keys` and `workload_measurements`.
- [x] Cryptographic SHA-256 token hashing and verification lifecycle (`POST`, `GET`, `DELETE` at `/api/user/api-keys`).
- [x] Frontend management console: **CLI & Workloads** tab with token generator, KPI cards, and live telemetry log.
- [x] Developer CLI commands: `carboniq config set-key`, `carboniq config set-url`, and `carboniq whoami`.

### 6. Sustainable Code Generation & AST Optimization
- [x] Modular Python library architecture (`carboniq/` and `pyproject.toml`).
- [x] `@carboniq.track` decorator and context manager with automatic telemetry transmission.
- [x] `@carboniq.defer_until_green` intelligent execution deferral governed by grid intensity thresholds.
- [x] `carboniq audit <file.py>`: AST static code analyzer detecting energy anti-patterns and scoring code A-F.
- [x] `carboniq optimize <file.py>`: Automated green code refactoring engine.
- [x] Comprehensive automated test coverage: `tests/test_e2e_user_flow.py` (30/30 assertions passing) and `tests/test_e2e_user_journey.py` (all lifecycle stages verified).

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