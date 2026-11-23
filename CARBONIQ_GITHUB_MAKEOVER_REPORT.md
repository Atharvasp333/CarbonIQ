# CarbonIQ — GitHub Repository Makeover, Branding & Attribution Report

**Branch:** `docs/official-branding-and-attribution`  
**Deployment Fork Remote:** [Kingslaye-varun/CarbonIQ_Capstone](https://github.com/Kingslaye-varun/CarbonIQ_Capstone/tree/docs/official-branding-and-attribution)  
**Upstream Team Remote:** [Atharvasp333/CarbonIQ](https://github.com/Atharvasp333/CarbonIQ)  
**Status:** **COMMITTED & PUSHED TO FORK — AWAITING USER APPROVAL TO OPEN PRs AND MERGE**

---

## 1. Summary of Completed Deliverables

All requested documentation, attribution, branding, and community governance files have been authored, validated, and committed:

| File | Status | Category | Purpose |
|---|---|---|---|
| [`CONTRIBUTION_AUDIT.md`](CONTRIBUTION_AUDIT.md) | **Completed** | Attribution | Comprehensive audit of commit history, Git authors, repository topology, and academic origin. |
| [`AUTHORS.md`](AUTHORS.md) | **Completed** | Authorship | Primary list of co-founders, roles, academic advisor, and authorship principles. |
| [`CONTRIBUTORS.md`](CONTRIBUTORS.md) | **Completed** | Attribution | All-Contributors standard contributor registry with categorized role badges. |
| [`.all-contributorsrc`](.all-contributorsrc) | **Completed** | Automation | Machine-readable All-Contributors specification file. |
| [`COPYRIGHT.md`](COPYRIGHT.md) | **Completed** | Legal / IP | Intellectual property disclosures, joint ownership analysis, licensing review, and third-party notices. |
| [`CITATION.cff`](CITATION.cff) | **Completed** | Academic | Validated CFF 1.2.0 metadata for GitHub's native "Cite this repository" feature. |
| [`CHANGELOG.md`](CHANGELOG.md) | **Completed** | Governance | Keep-a-Changelog record distinguishing released v0.2.0 features from planned milestones. |
| [`ROADMAP.md`](ROADMAP.md) | **Completed** | Governance | Technical roadmap spanning current v0.2.0, Q1 2027 (v0.3.0), and long-term milestones. |
| [`SECURITY.md`](SECURITY.md) | **Completed** | Security | Vulnerability reporting procedure, supported version tiers, and security practices. |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | **Completed** | Community | Local development, test execution, conventional commits, and PR workflow guidelines. |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | **Completed** | Community | Professional standards, harassment-free pledge, and enforcement responsibilities. |
| [`.github/ISSUE_TEMPLATE/bug_report.yml`](.github/ISSUE_TEMPLATE/bug_report.yml) | **Completed** | GitHub Templates | Structured YAML bug report issue form. |
| [`.github/ISSUE_TEMPLATE/feature_request.yml`](.github/ISSUE_TEMPLATE/feature_request.yml) | **Completed** | GitHub Templates | Structured YAML feature request form. |
| [`.github/pull_request_template.md`](.github/pull_request_template.md) | **Completed** | GitHub Templates | Comprehensive PR submission checklist and summary template. |
| [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md) | **Completed** | Technical Docs | Verified installation, CLI commands, AST optimization, and telemetry sync guide. |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | **Completed** | Technical Docs | Multi-tier architecture overview with Mermaid diagrams of multi-agent and CLI pipelines. |
| [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) | **Completed** | Technical Docs | Developer setup, automated test execution, and wheel isolation verification guide. |
| [`README.md`](README.md) | **Completed** | Project Presentation | Full redesign with badges, architecture diagrams, CLI references, and disclosures. |
| [`pyproject.toml`](pyproject.toml) | **Completed** | Metadata | Enriched `[project.urls]` with Bug Tracker and Changelog (version kept stable at `0.2.0`). |

---

## 2. Contributor Attribution Verification

The audit confirms that CarbonIQ was developed as a final-year academic capstone project at Vivekanand Education Society's Institute of Technology (VESIT), Mumbai, by a four-member student team under the academic guidance of Mrs. Charusheela Nehete:

1. **Atharva Pingale (@Atharvasp333):**
   * *Designation:* Core Developer — Cloud & AI Architecture
   * *Verified Roles:* Upstream Repository Maintainer.
   * *Codebase Ownership:* Multi-agent cloud emissions analysis architecture (`backend/agents/`), AWS Cost and Usage Report (CUR) processing/ingestion, backend agent orchestration, carbon emission accounting, and cloud-side intelligence via Google Gemini.
2. **Varun Rahatgaonkar (@Kingslaye-varun):**
   * *Designation:* Core Developer — Python SDK, Developer Tools & Release Engineering
   * *Verified Roles:* Deployment & PyPI Release Fork Maintainer.
   * *Codebase Ownership:* CarbonIQ Python SDK packaging (PEP 517/518/621), CLI architecture, AST-based sustainable code analysis and optimization (`carboniq/optimizer.py`, `carboniq audit`, `carboniq optimize`), VS Code developer tooling (`vscode-extension/`), deployment integration, GitHub Actions CI/CD release engineering, PyPI OIDC Trusted Publishing, and automated release verification.
   * *Verified Contribution Statement:* *"Varun Rahatgaonkar (@Kingslaye-varun) — CarbonIQ SDK release engineering, packaging, deployment integration, CI/CD, and developer tooling contributions."*
3. **Nidhi Puthran (@nidhi0810):**
   * *Designation:* Core Developer — Carbon-Aware Computing
   * *Codebase Ownership:* Green Software Foundation Carbon Aware SDK client (`cli/carbon_aware_sdk.py`), regional grid carbon intensity functionality, AI deployment analysis API (`backend/routes/deployment_analysis.py`), regional and temporal decision support (`carboniq deploy-analysis`, `carboniq carbon-intensity`), and multi-service development launch scripts (`start-dev.ps1`).
4. **Tanaya Jain (@tanaya2005):**
   * *Designation:* Research, Documentation & Intellectual Property
   * *Project Contributions:* Capstone project master blackbook documentation, research paper preparation (`docs/paper/main.tex`), academic milestone reports and project documentation updates, intellectual property rights (IPR) documentation, and logo copyright-related preparation and filing work (where supported by project records).
   * *Additional Git-verified Commits:* Frontend authentication UI layouts (`Login.jsx`, `Signup.jsx`, `Home.jsx`), Fernet credential encryption helper (`backend/services/crypto.py`), and AWS credentials database routes (`backend/routes/aws_credentials.py`).
5. **Mrs. Charusheela Nehete:**
   * *Designation:* Assistant Professor, Department of Information Technology, VESIT
   * *Role:* Academic Project Guide & Faculty Advisor (research methodology supervision, architectural review, and capstone evaluation).

---

## 3. Existing License & Copyright Findings

* **Current State:** `pyproject.toml` in published `carboniq-sdk==0.2.0` declares `license = { text = "MIT" }` and Trove classifier `License :: OSI Approved :: MIT License`.
* **Licensing Recommendation:** Retaining the **MIT License** attributed to **The CarbonIQ Authors and Contributors** is recommended to preserve consistency with the published PyPI v0.2.0 metadata:
  ```
  Copyright (c) 2026 The CarbonIQ Authors and Contributors
  ```
* **Non-Exclusivity:** Publishing on PyPI or maintaining the deployment fork under `@Kingslaye-varun` reflects authorized release engineering and does not establish exclusive legal ownership over the co-authored codebase.
* **Software vs. Logo IP:** Software code is governed by the permissive MIT License; logo/branding design documentation represents distinct project assets.

---

## 4. Documentation & Community Validation Results

* **Markdown Links:** All internal links across all Markdown files resolve cleanly (0 broken links).
* **YAML Validation:** `.github/ISSUE_TEMPLATE/bug_report.yml`, `.github/ISSUE_TEMPLATE/feature_request.yml`, and `CITATION.cff` verified 100% valid YAML via `yaml.safe_load`.
* **Automated Tests:** All **36 automated unit, CLI, packaging isolation, and grid integration tests PASSED** in 14.15s (`pytest tests/test_sdk_api.py tests/test_cli_commands.py tests/test_packaging_and_security.py tests/test_carbon_aware_integration.py -v`).
* **Package Isolation:** Verified zero generic `cli` namespace collision in `site-packages`.
* **Security & Secret Scan:** Verified zero private keys, API keys, or active credentials tracked in Git.

---

## 5. Two-Repository Synchronization Plan

* **Deployment Fork (`Kingslaye-varun/CarbonIQ_Capstone`):**
  * Branch `docs/official-branding-and-attribution` is pushed and ready for Pull Request creation:
  * PR URL: [https://github.com/Kingslaye-varun/CarbonIQ_Capstone/pull/new/docs/official-branding-and-attribution](https://github.com/Kingslaye-varun/CarbonIQ_Capstone/pull/new/docs/official-branding-and-attribution)
* **Upstream Repository (`Atharvasp333/CarbonIQ`):**
  * As instructed by the safety protocol, no direct push has been made to `origin/main`.
  * A Pull Request can be submitted from `Kingslaye-varun/CarbonIQ_Capstone:docs/official-branding-and-attribution` targeting `Atharvasp333/CarbonIQ:main`.
