# CarbonIQ Project Status Update — Implemented Features

This document provides a comprehensive summary of all features, services, and database schemas currently implemented in the **CarbonIQ** project. Use this update as a starting point to plan the final phase of development.

---

## 🚀 1. Frontend Architecture & UI Screens (React 19 + Vite + Tailwind CSS)

The frontend is built using **React 19**, styled with **Tailwind CSS**, and uses **React Router 7** for routing. Key screens and components include:

### 🔑 Authentication (`src/pages/auth/`)
*   **Login & Signup Pages (`Login.jsx`, `Signup.jsx`)**: Connected to the backend authentication router. Supports custom JWT session management and integrates with **Neon Auth** UI components.
*   **Protected Routes (`src/routes/ProtectedRoute.jsx`)**: Ensures user sessions are verified before accessing the application dashboard.

### 📊 Dashboard & Reports (`src/pages/main/`)
*   **Home Dashboard (`Home.jsx`)**:
    *   **AWS Connect Banner (`AWSConnectBanner.jsx`)**: Prompts users to configure their AWS account once, fetching credentials dynamically.
    *   **CSV Upload Section (`UploadSection.jsx`)**: Allows manual drag-and-drop or file upload of AWS CUR reports.
    *   **Data Aggregation**: Highlights high-level metrics like *Total Emissions (kg CO₂)*, *Total Cost ($)*, and *Energy Used (kWh)* immediately after CSV/S3 processing.
*   **Reports (`Reports.jsx`)**:
    *   Uses **Recharts** to plot time-series trend lines for both emissions and cloud spend.
    *   **Scope Analysis (`ScopeAnalysis.jsx`)**: Displays emission breakdowns across Scope 1, Scope 2, and Scope 3.
    *   Provides interactive daily and monthly aggregation tabs.
*   **Services drill-down (`Services.jsx` & `ServiceDetail.jsx`)**:
    *   Lists emission impact per AWS service (EC2, RDS, S3, Lambda).
    *   Contains detailed charts highlighting usage metrics, cost analysis, and carbon intensity per service resource.

### 💡 Sustainability Intelligence (`Insights.jsx`)
*   Provides a clean dashboard showing AI-generated carbon reduction suggestions.
*   Includes filtering of recommendations by **Category** (Compute, Storage, Region, Time-Shifting) and **Confidence Score** (High, Medium, Low).
*   Integrates a **What-If Simulator (`WhatIfSimulator.jsx`)** that allows interactive modeling of scenario changes (e.g., migrating regions or downsizing instance types) showing instant projected carbon and cost savings.

### ⚙️ Settings & Profiles
*   **Organization Profile (`OrganizationProfile.jsx`)**: Questionnaire capturing constraints (e.g., latency sensitivity, workload region limits, migration flexibility) that the AI recommendation engine uses to validate carbon-reduction strategies.
*   **Settings (`Settings.jsx`) & Profile (`Profile.jsx`)**: Standard password changes, AWS credential management, and user configuration.

### 💬 CarbonIQ AI Chatbot (`src/components/ChatBot/`)
*   An interactive chat window utilizing **Google Gemini** to answer questions specifically about AWS carbon footprints, green architecture, and emission reductions. Protected by keyword filters to ensure conversations remain focused on sustainability.

---

## ⚙️ 2. Backend Architecture & Multi-Agent System (FastAPI + Python 3.12)

The backend is built with **FastAPI** and uses a modular multi-agent structure. The system is split into two distinct engines that coordinate via the database.

### 🏭 Engine 1: Carbon Accounting Engine (`backend/agents/accounting/`)
Answers: **"What happened?"**
1.  **Ingestion Agent (`csv_agent.py` & `compression_agent.py`)**:
    *   Parses AWS Cost & Usage Reports (CUR).
    *   Compresses raw files (e.g., 5,000+ hourly line items compressed into ~200 daily/resource records) by grouping by service, region, and day.
2.  **Region Mapping Agent (`region_mapping_agent.py`)**:
    *   Maps AWS regions (e.g., `ap-south-1`) to regional electricity grid zones (e.g., `IN-WE` for Western India).
3.  **Carbon Intensity Agent (`carbon_intensity_agent.py`)**:
    *   Queries grid intensity rates (gCO₂/kWh) using the **Electricity Maps API**.
    *   Implements caching by zone & date to limit API calls and uses regional fallback values if keys are missing.
4.  **Emission Calculation Agent (`emission_calculation_agent.py`)**:
    *   Applies service-specific power factors (e.g., EC2: `0.15 kWh/hr`, Lambda: `0.0001 kWh/GB-s`, S3: `0.0005 kWh/GB`) and multiplies by grid intensity to calculate final carbon weight.
5.  **Analysis Summary Agent (`analysis_summary_agent.py`)**:
    *   Generates the aggregated metrics and structures the payload for frontend visualization.

### 🧠 Engine 2: Sustainability Intelligence Engine (`backend/agents/intelligence/`)
Answers: **"What should we do?"**
1.  **Workload Analysis Agent (`workload_analysis_agent.py`)**: Scans historical usage to identify key resource workloads and compute-intensive operations.
2.  **Pattern Detection Agent (`pattern_detection_agent.py`)**: Identifies idle servers, storage hotspots, or off-peak usage windows.
3.  **Optimization Agent (`optimization_agent.py`)**: Proposes concrete changes like region migration or downsizing.
4.  **Constraint Validation Agent (`constraint_validation_agent.py`)**: Filters options against the user's organization profile (e.g., rejects region migration suggestions if the user requires low latency or local compliance).
5.  **Recommendation & Explanation Agents (`recommendation_agent.py` & `explanation_agent.py`)**: Formulates final recommendations and generates natural language explanations using **Google Gemini**.

---

## 🗄️ 3. Database Schema (NeonDB / PostgreSQL)

Integrated using `asyncpg` for non-blocking FastAPI queries. All tables are fully initialized on startup:

*   `users`: Stores names, hashed passwords (bcrypt), and account creation timestamps.
*   `aws_credentials`: Stores access/secret keys (encrypted via Fernet) mapped to S3 bucket configurations.
*   `analyses`: Logs file metadata, total emissions, total cost, and energy consumed.
*   `emission_records`: Detailed row-by-row resource emissions, zone codes, and intensity sources.
*   `api_call_logs`: Logs response latency and status for all outbound carbon intensity requests.
*   `organization_profile`: Mapped 1:1 to users, storing workload latency and migration rules.
*   `analysis_summary`: Precomputed dashboard views stored in JSONB to ensure sub-second dashboard loading.
*   `recommendation_runs`: Caches AI recommendations, confidence scores, and findings.
*   `user_insights`: Aggregated trends, month-on-month targets, and alerts.
*   `audit_log`: Logs user actions, request IPs, and updates.

---

## 🔗 4. External Integrations
*   **AWS S3 Integration (`services/s3_fetcher.py`)**:
    *   Queries AWS buckets using `boto3`.
    *   Supports automatic extraction and decompressive reading of gzip files (`.csv.gz`).
    *   Implements auto-discovery to automatically locate the newest CUR file in the specified bucket.
*   **Electricity Maps API (`services/electricity_maps.py`)**: Historical & real-time carbon intensity rates per grid zone.
*   **Google Gemini AI (`services/gemini.py`)**: Used for the conversational chatbot and the generation of tailored, context-aware optimization advice.

---

## 📝 5. Gaps & Remaining Features (To-Do List)

To complete the project, the following features from the to-do roadmap should be addressed next:

1.  **Dashboard Export (PDF Reports)**: Implement generating downloadable PDF files summarizing carbon footprint reports.
2.  **Physical Feasibility Validation**: Ensure the optimization logic flags complexity for regional migrations (e.g., warning users that DynamoDB or API Gateways cannot be trivially moved across regions compared to EC2 instances).
3.  **Efficiency Streaks & Gamification**: Store login logs and track continuous green improvements to award carbon-reduction "streaks" to users.
4.  **Role-Based Access Control**: Differentiate permissions between standard users and organization administrators.
5.  **Dark Mode Toggle**: Implement a theme context to switch between light and dark UI variants.
6.  **Redundant Routes Cleanup**: Standardize and refactor route files (like `routes/multi_agent_analysis.py` vs `routes/aws_integration.py`) to reduce duplication.
