# Authors of CarbonIQ

CarbonIQ was conceived and developed as an academic capstone initiative at Vivekanand Education Society's Institute of Technology (VESIT), Mumbai, under the academic mentorship of Mrs. Charusheela Nehete and advisory review from Tata Consultancy Services (TCS) mentors.

The project is co-founded and maintained by its four principal creators:

---

## Core Maintainers & Co-Founders

### Atharva Pingale
* **GitHub:** [@Atharvasp333](https://github.com/Atharvasp333)
* **Role:** Project Co-Founder & Upstream Repository Maintainer
* **Key Contributions:**
  * Multi-agent cloud accounting and intelligence architecture (`backend/agents/`).
  * Ingestion, region-mapping, carbon intensity, and emission calculation agents.
  * LLM-driven sustainability insights with Google Gemini.
  * Original upstream repository administrator ([Atharvasp333/CarbonIQ](https://github.com/Atharvasp333/CarbonIQ)).

### Varun Rahatgaonkar
* **GitHub:** [@Kingslaye-varun](https://github.com/Kingslaye-varun)
* **Role:** Project Co-Founder & SDK Release Maintainer
* **Key Contributions:**
  * CarbonIQ SDK release engineering, PEP 621 packaging, and PyPI OIDC Trusted Publishing.
  * AST-based Sustainable Code Auditor and green refactoring engine (`carboniq/optimizer.py`, `carboniq audit`, `carboniq optimize`).
  * Visual Studio Code Extension for inline carbon linting and green code actions.
  * Developer CLI architecture, multi-tenant user profile synchronization, and test automation.
  * Deployment and PyPI release fork administrator ([Kingslaye-varun/CarbonIQ_Capstone](https://github.com/Kingslaye-varun/CarbonIQ_Capstone)).

### Tanaya Jain
* **GitHub:** [@tanaya2005](https://github.com/tanaya2005)
* **Role:** Project Co-Founder & Security Lead
* **Key Contributions:**
  * At-rest credential encryption using Fernet/AES (`backend/services/crypto.py`).
  * User authentication flows and session management with Neon Auth (`backend/routes/auth.py`).
  * Secure AWS CUR S3 credential storage and database integration (`backend/routes/aws_credentials.py`).
  * Frontend AWS Connect integration banner and credential state management.

### Nidhi Puthran
* **GitHub:** [@nidhi0810](https://github.com/nidhi0810)
* **Role:** Project Co-Founder & Carbon-Aware Computing Lead
* **Key Contributions:**
  * Green Software Foundation Carbon Aware SDK client (`cli/carbon_aware_sdk.py`).
  * AI-driven cloud deployment analysis API (`backend/routes/deployment_analysis.py`).
  * CLI deployment commands (`carboniq deploy-analysis` and `carboniq carbon-intensity`).
  * Multi-region carbon intensity forecasting and local development orchestration scripts (`start-dev.ps1`).

---

## Academic Guidance

* **Mrs. Charusheela Nehete** — Faculty Advisor, Department of Information Technology, Vivekanand Education Society's Institute of Technology (VESIT).
  * Provided research supervision, architectural feedback, and methodology evaluation.

---

## Authorship Principles

1. **Shared Heritage:** All code written during the collaborative capstone project is the collective intellectual creation of the authors.
2. **Fair Attribution:** No single maintainer claims exclusive ownership over the shared platform.
3. **Release Maintainership:** Repository or package maintainership (such as hosting deployment forks or managing PyPI publishing credentials) constitutes operational service to the project and does not diminish or reassign co-authors' moral and legal attribution.
