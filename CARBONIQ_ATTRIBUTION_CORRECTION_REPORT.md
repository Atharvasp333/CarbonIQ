# CarbonIQ — Final Attribution Correction Report

**Working Branch:** `docs/official-branding-and-attribution`  
**Date:** 2026-11-23  
**Status:** **COMMITTED & VERIFIED — READY FOR REVIEW & PULL REQUEST CREATION**  
**Repositories:**
- Deployment Fork: [Kingslaye-varun/CarbonIQ_Capstone](https://github.com/Kingslaye-varun/CarbonIQ_Capstone)
- Upstream Team: [Atharvasp333/CarbonIQ](https://github.com/Atharvasp333/CarbonIQ)

---

## 1. Executive Summary & Purpose

This correction initiative was executed to resolve factual inaccuracies in earlier drafts regarding external mentorship claims, ensure truthful and fair representation of the student team's contributions, and align repository attribution with genuine Git history and academic capstone records.

---

## 2. False Mentorship Claims Removed

All statements alleging corporate sponsorship, mentorship, advisory review, or technical guidance by Tata Consultancy Services (TCS) have been completely excised from the repository.

### Summary of Removals:
* **`README.md`:** Removed TCS acknowledgment under the Acknowledgments section; updated to attribute guidance solely to faculty advisor Mrs. Charusheela Nehete.
* **`AUTHORS.md`:** Removed all references to TCS mentorship; replaced with the standardized academic capstone description.
* **`CONTRIBUTION_AUDIT.md`:** Completely purged former mentorship claims; added explicit clarification that external exploratory discussions were separate from CarbonIQ's scope and did not constitute project mentorship, sponsorship, or institutional affiliation.
* **`COPYRIGHT.md`:** Removed all external corporate mentions; reiterated that no intellectual property was assigned to any external commercial entity.
* **`CONTRIBUTORS.md` & `.all-contributorsrc`:** Removed external mentorship badges and entries.
* **`CARBONIQ_GITHUB_MAKEOVER_REPORT.md`:** Updated all sections to eliminate legacy mentions.

### Canonical Academic Capstone Description:
> *"CarbonIQ was developed as a final-year academic capstone project at Vivekanand Education Society's Institute of Technology (VESIT), Mumbai, by a four-member student team under the academic guidance of Mrs. Charusheela Nehete."*

---

## 3. Corrected Team Designations & Component Attributions

Each contributor's designation and scope of work has been aligned with actual Git commit logs and academic capstone documentation:

### 1. Varun Rahatgaonkar (@Kingslaye-varun)
* **Designation:** Core Developer — Python SDK, Developer Tools & Release Engineering
* **Verified Contributions:**
  * CarbonIQ Python SDK packaging (PEP 517/518/621) and PyPI public release maintainership.
  * CLI architecture, command integrations, and client communication.
  * AST-based sustainable code analysis and automated green refactoring engine (`carboniq/optimizer.py`, `carboniq audit`, `carboniq optimize`).
  * Visual Studio Code developer tooling (`vscode-extension/`).
  * Cloud deployment integration on Vercel and Render.
  * GitHub Actions CI/CD release engineering and PyPI OIDC Trusted Publishing.
  * Automated release verification test suites.

### 2. Atharva Pingale (@Atharvasp333)
* **Designation:** Core Developer — Cloud & AI Architecture
* **Verified Contributions:**
  * Multi-agent cloud emissions analysis architecture (`backend/agents/`).
  * AWS Cost and Usage Report (CUR) processing, filtering, and ingestion normalization.
  * Backend agent orchestration and inter-agent data passing.
  * Carbon emission accounting, regional intensity lookup, and Scope 2 calculation math.
  * Cloud-side explainable intelligence and recommendations via Google Gemini.
  * Upstream repository administrator for [Atharvasp333/CarbonIQ](https://github.com/Atharvasp333/CarbonIQ).

### 3. Nidhi Puthran (@nidhi0810)
* **Designation:** Core Developer — Carbon-Aware Computing
* **Verified Contributions:**
  * Green Software Foundation Carbon Aware SDK client integration (`cli/carbon_aware_sdk.py`).
  * Regional electric grid carbon intensity querying functionality.
  * Carbon-aware deployment analysis API (`backend/routes/deployment_analysis.py`).
  * Regional and temporal decision support commands (`carboniq deploy-analysis`, `carboniq carbon-intensity`).
  * Multi-service development launch script (`start-dev.ps1`).

### 4. Tanaya Jain (@tanaya2005)
* **Designation:** Research, Documentation & Intellectual Property
* **Verified Contributions:**
  * Capstone project master blackbook compilation (`docs/Blackbook_Group13_CarbonIQ.pdf`).
  * Research paper preparation and technical documentation (`docs/paper/main.tex`).
  * Academic milestone reports and project documentation updates (`carboniq-update1.md`).
  * Intellectual property rights (IPR) documentation.
  * Logo copyright-related preparation and filing work (where supported by project records).
  * *Additional Git-verified Commits:* Frontend authentication UI layouts (`Login.jsx`, `Signup.jsx`, `Home.jsx`), Fernet credential encryption helper (`backend/services/crypto.py`), and AWS credentials storage routes (`backend/routes/aws_credentials.py`).

### 5. Mrs. Charusheela Nehete
* **Designation:** Assistant Professor, Department of Information Technology, VESIT, Mumbai
* **Role:** Academic Project Guide & Faculty Advisor (research supervision, architectural review, and capstone evaluation).

---

## 4. Attribution Evidence Matrix

| Contributor | Contribution Area | Specific Deliverables | Git / Document Evidence | Verification Status |
|---|---|---|---|---|
| **Atharva Pingale** | Cloud Multi-Agent Accounting Architecture | 6-Agent accounting pipeline, orchestrator, ingestion, carbon intensity & emission agents, Google Gemini integration | Git commits `7685d64`, `1f89304`, `backend/agents/` | **Verified by Git** |
| **Atharva Pingale** | Upstream Repository Management | Original repository creation, initial commit tree, issue tracking | GitHub upstream remote `Atharvasp333/CarbonIQ` | **Verified by Git** |
| **Atharva Pingale** | Academic Research Paper | Co-author on capstone research preprint | `docs/paper/main.tex` author list | **Verified by project document** |
| **Varun Rahatgaonkar** | Python SDK Packaging & PyPI Launch | PEP 517/518/621 packaging, GitHub Actions OIDC Trusted Publishing, PyPI `carboniq-sdk` v0.2.0 | Git commits `54821a9` to `1a95251`, `.github/workflows/release.yml`, PyPI release | **Verified by Git** |
| **Varun Rahatgaonkar** | AST Sustainable Code Optimizer | `carboniq/optimizer.py`, `carboniq audit`, `carboniq optimize`, AST refactoring engine | Git commits `66fbf38`, `2e35299`, `carboniq/optimizer.py` | **Verified by Git** |
| **Varun Rahatgaonkar** | VS Code Extension & Developer Tooling | Inline AST linting, code actions, CLI architecture, automated test suites (36 tests) | Git commits `b311e39`, `6ffaeb7`, `vscode-extension/`, `tests/` | **Verified by Git** |
| **Varun Rahatgaonkar** | Academic Research Paper | Co-author on capstone research preprint | `docs/paper/main.tex` author list | **Verified by project document** |
| **Nidhi Puthran** | Carbon-Aware Computing | Green Software Foundation Carbon Aware SDK client, regional grid intensity lookup | Git commit `c5bc5f0`, branch `origin/final-nidhi-carboniq`, `cli/carbon_aware_sdk.py` | **Verified by Git** |
| **Nidhi Puthran** | AI Deployment Analysis & CLI | `/api/cli/deploy-analysis`, `carboniq deploy-analysis`, `carboniq carbon-intensity`, `start-dev.ps1` | Git commit `c5bc5f0`, `backend/routes/deployment_analysis.py` | **Verified by Git** |
| **Nidhi Puthran** | Academic Research Paper | Co-author on capstone research preprint | `docs/paper/main.tex` author list | **Verified by project document** |
| **Tanaya Jain** | Capstone Blackbook & Academic Documentation | Master capstone blackbook compilation, academic progress updates, testing documentation | Project reports, `docs/Blackbook_Group13_CarbonIQ.pdf`, `carboniq-update1.md` | **Verified by project document / Team-reported** |
| **Tanaya Jain** | Research Paper Preparation | Co-author on capstone research preprint | `docs/paper/main.tex` author list | **Verified by project document** |
| **Tanaya Jain** | Intellectual Property & Logo Work | IPR documentation, logo copyright-related preparation and filing work | Team capstone reports | **Team-reported** *(Formal registration grant unverified)* |
| **Tanaya Jain** | Frontend UI & Credential Security Commits | UI page layouts (`Login.jsx`, `Signup.jsx`, `Home.jsx`), Fernet crypto helper (`crypto.py`), AWS credentials route commits | Git commits `fedcbf1`, `b4f2251`, `6161ea8`, `928ad13`, `7a608b1` | **Verified by Git** |
| **Mrs. Charusheela Nehete** | Academic Faculty Guidance | Capstone faculty guide and advisor, methodology oversight | `docs/paper/main.tex` author list, VESIT project guide record | **Verified by project document** |

---

## 5. Remaining Uncertainties & Legal Disclaimers

1. **Logo Copyright Registration:**
   * While preparatory copyright filing documentation was compiled by Tanaya Jain, an official government copyright registration certificate or registration number has not been provided.
   * *Status:* Documented as **Team-reported / Unverified** pending physical certificate records. No unverified claim of a granted copyright registration is made.
2. **Software Code Licensing vs Logo IP:**
   * Software algorithms, CLI, SDK, and multi-agent backend remain licensed under the open-source **MIT License**.
   * Logo/brand design assets are distinct from the software code.
3. **MIT License Notice Formulation:**
   * Recommended copyright holder line for root LICENSE:
     ```
     Copyright (c) 2026 The CarbonIQ Authors and Contributors
     ```
   * Reflects collaborative co-authorship without creating individual or exclusive legal assertions.

---

## 6. Files Corrected in Working Branch

| File | Nature of Correction |
|---|---|
| `AUTHORS.md` | Removed TCS claims; updated roles to reflect Tanaya's documentation/IPR leadership and core dev roles. |
| `CONTRIBUTORS.md` | Removed TCS mentorship references; updated contributor badges and descriptions. |
| `.all-contributorsrc` | Corrected contribution tags (`doc`, `research`, `code`, `design`). |
| `CONTRIBUTION_AUDIT.md` | Added exhaustive attribution matrix, academic origin description, and complete removal of TCS claims. |
| `COPYRIGHT.md` | Removed corporate mentions; clarified distinction between software copyright and logo IP work. |
| `README.md` | Replaced legacy contributor table and acknowledgments with verified academic capstone attribution. |
| `CARBONIQ_GITHUB_MAKEOVER_REPORT.md` | Synchronized report with corrected contributor descriptions. |

---

## 7. Verification Results

* **Automated Unit & Integration Tests:** All **36 tests PASSED** in 14.15s (`pytest tests/test_sdk_api.py tests/test_cli_commands.py tests/test_packaging_and_security.py tests/test_carbon_aware_integration.py -v`).
* **Markdown Links:** All links resolve cleanly (0 broken links).
* **YAML Validation:** `.github/ISSUE_TEMPLATE/*.yml` and `CITATION.cff` verified 100% valid YAML.
* **Code Isolation:** Application logic, PyPI v0.2.0 packaging, and release workflows remain completely untouched.
