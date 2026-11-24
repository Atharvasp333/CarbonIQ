# Authors of CarbonIQ

CarbonIQ originated as the Group 13 Information Technology Capstone Project (Academic Year 2026–27) at Vivekanand Education Society's Institute of Technology (VESIT), Mumbai, under the academic guidance of Mrs. Charusheela Nehete.

---

## Core Project Team & Co-Founders

### Atharva Pingale
* **GitHub:** [@Atharvasp333](https://github.com/Atharvasp333)
* **Designation:** Core Developer — Cloud & AI Architecture
* **Upstream Maintainer:** Administrator of the original upstream repository ([Atharvasp333/CarbonIQ](https://github.com/Atharvasp333/CarbonIQ))
* **Contributions:**
  * Multi-agent cloud emissions analysis architecture (`backend/agents/`).
  * AWS Cost and Usage Report (CUR) processing, filtering, and ingestion normalization.
  * Backend agent engine orchestration and inter-agent communication.
  * Carbon emission accounting, regional intensity lookup, and Scope 2 calculation math.
  * Cloud-side explainable intelligence and recommendations via Google Gemini.

### Varun Rahatgaonkar
* **GitHub:** [@Kingslaye-varun](https://github.com/Kingslaye-varun)
* **Designation:** Group 13 Team Leader, Core Developer — Python SDK, Developer Tools & Release Engineering
* **Academic Leadership:** Group 13 Team Leader for the 2026–27 Department of Information Technology capstone project at VESIT (project planning, cross-tier integration, and release stewardship).
* **Deployment & Release Maintainer:** Administrator of the deployment and PyPI publishing repository ([Kingslaye-varun/CarbonIQ_Capstone](https://github.com/Kingslaye-varun/CarbonIQ_Capstone))
* **Contributions:**
  * CarbonIQ Python SDK packaging (PEP 517/518/621) and public release maintainership.
  * CLI architecture, command implementations, and client integration.
  * AST-based sustainable code analysis and automated green refactoring engine (`carboniq/optimizer.py`, `carboniq audit`, `carboniq optimize`).
  * Visual Studio Code developer tooling (`vscode-extension/`).
  * Production deployment integration on Vercel and Render.
  * GitHub Actions CI/CD release engineering and PyPI OpenID Connect (OIDC) Trusted Publishing.
  * Automated release verification test suites.

### Nidhi Puthran
* **GitHub:** [@nidhi0810](https://github.com/nidhi0810)
* **Designation:** Core Developer — Carbon-Aware Computing
* **Contributions:**
  * Green Software Foundation Carbon Aware SDK client integration (`cli/carbon_aware_sdk.py`).
  * Regional electric grid carbon intensity querying functionality.
  * Carbon-aware deployment analysis API (`backend/routes/deployment_analysis.py`).
  * Regional and temporal decision support commands (`carboniq deploy-analysis`, `carboniq carbon-intensity`).
  * Multi-service development launch script (`start-dev.ps1`).

### Tanaya Jain
* **GitHub:** [@tanaya2005](https://github.com/tanaya2005)
* **Designation:** Research, Documentation & Intellectual Property
* **Contributions:**
  * Capstone project master blackbook documentation.
  * Research paper preparation and technical documentation.
  * Academic milestone reports and project documentation updates.
  * Intellectual property rights (IPR) documentation.
  * Logo copyright-related preparation and filing work (where supported by project records).
  * *Additional Git-verified contributions:* Frontend authentication UI layouts (`Login.jsx`, `Signup.jsx`, `Home.jsx`), Fernet credential encryption helper (`backend/services/crypto.py`), and AWS credentials storage routes.

---

## Academic Project Guidance

* **Mrs. Charusheela Nehete**
  * **Designation:** Assistant Professor / Faculty Guide, Department of Information Technology, Vivekanand Education Society's Institute of Technology (VESIT), Mumbai, India.
  * **Role:** Academic project advisor, methodology supervision, architectural review, and capstone evaluation.

---

## Authorship & Attribution Principles

1. **Shared Academic Origin:** The project originated as a collaborative final-year academic capstone project (Group 13, AY 2026–27) at VESIT.
2. **Factual Attribution:** Responsibilities and contributions are documented truthfully according to verified Git commit history and academic project records.
3. **No Exclusive Claims:** Release engineering and repository administration responsibilities (such as managing the deployment fork or publishing `carboniq-sdk` to PyPI) represent operational maintenance and do not constitute exclusive legal ownership of the collaborative project.
4. **Project Repositories & Academic Context:** The institutional academic documentation is archived at [itprojects-create/Cp_13_2026-27](https://github.com/itprojects-create/Cp_13_2026-27). Team leader and release maintainer roles reflect project coordination and distribution logistics; they do not alter the collective authorship of the software.
