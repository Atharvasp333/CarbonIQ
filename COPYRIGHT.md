# CarbonIQ — Copyright, Licensing & Ownership Statement

**Effective Date:** November 2026  
**Project:** CarbonIQ (Unified Cloud & Developer Carbon Intelligence Platform)  
**Distribution:** `carboniq-sdk` on PyPI  

---

## 1. Copyright Ownership Principles

The intellectual property, architecture, source code, and technical documentation of CarbonIQ are the joint creation of its co-founders:

* **Atharva Pingale** ([@Atharvasp333](https://github.com/Atharvasp333))
* **Varun Rahatgaonkar** ([@Kingslaye-varun](https://github.com/Kingslaye-varun))
* **Tanaya Jain** ([@tanaya2005](https://github.com/tanaya2005))
* **Nidhi Puthran** ([@nidhi0810](https://github.com/nidhi0810))

Under international copyright conventions and Indian copyright law, collaborative works developed jointly without a formal corporate assignment agreement remain the joint property of all participating co-authors.

### Important Ownership Clarifications
1. **Repository Hosting:** Hosting the deployment fork or continuous deployment workflows at `Kingslaye-varun/CarbonIQ_Capstone` does not establish exclusive legal copyright over the codebase.
2. **PyPI Publishing:** Publishing `carboniq-sdk` to PyPI using GitHub Actions OIDC Trusted Publishing under `@Kingslaye-varun` reflects release engineering and distribution maintainership. It does not transfer or extinguish co-authors' copyright ownership.
3. **No Commercial Assignment:** The project has not been assigned or sold to any corporation or third party. Advisory mentorship by Tata Consultancy Services (TCS) mentors was academic; TCS makes no claim of institutional copyright or trademark over CarbonIQ.

---

## 2. Personal Contribution Verification & Acknowledgment

As verified against the Git commit history and pull request audit:

> **"Varun Rahatgaonkar (@Kingslaye-varun) — CarbonIQ SDK release engineering, packaging, deployment integration, CI/CD, and developer tooling contributions."**

*Verified Scope of Work:*
* Spearheaded PEP 621 packaging for `carboniq-sdk` and configured GitHub Actions OIDC Trusted Publishing.
* Designed and implemented the AST Sustainable Code Optimizer engine (`carboniq/optimizer.py`, `carboniq audit`, `carboniq optimize`).
* Developed the CarbonIQ Visual Studio Code Extension (`vscode-extension/`).
* Engineered developer CLI features, multi-tenant user profile synchronization, and automated test suites (`tests/`).
* Configured and verified production cloud integrations on Vercel and Render.

---

## 3. Project Licensing Recommendation & Analysis

### Current Status
* `pyproject.toml` in version 0.2.0 declares `license = { text = "MIT" }` with the Trove classifier `License :: OSI Approved :: MIT License`.
* The published `carboniq-sdk==0.2.0` wheel and source archive on PyPI carry this MIT declaration.
* To provide complete transparency and avoid license ambiguity, a formal root `LICENSE` file has been added using the MIT License attributed to **The CarbonIQ Authors and Contributors**.

### License Options for Future Releases (v0.3.0+)

| License | Advantages | Considerations | Recommendation |
|---|---|---|---|
| **MIT License** *(Current)* | Maximum adoption, extremely permissive, standard across Python developer tools, matches v0.2.0 PyPI metadata. | Does not include an explicit patent grant or trademark clause. | **Recommended for retention** to preserve continuity with published v0.2.0 artifacts. |
| **Apache-2.0** | Permissive, includes explicit patent license and retaliation provisions; strong for cloud/enterprise tools. | Slightly more complex notices; changing from MIT to Apache-2.0 requires agreement from all 4 co-authors and a new PyPI release (v0.3.0). | Strong candidate for v0.3.0+ if formal patent protection is desired. |
| **AGPL-3.0** | Strong copyleft; prevents proprietary hosted SaaS forks without releasing source code. | Discourages commercial adoption and integration into corporate CI/CD pipelines; incompatible with MIT v0.2.0 metadata without full re-licensing. | Not recommended for an SDK/developer toolkit. |

### Impact on Published PyPI Package (v0.2.0)
* PyPI release artifacts are immutable once published. The v0.2.0 distribution metadata cannot and should not be modified on PyPI.
* If the maintainers collectively choose to adopt a different license (e.g., Apache-2.0), that change will formally take effect in the **next release** (e.g., `v0.3.0`) with updated `pyproject.toml` metadata and classifiers.

---

## 4. Third-Party Licenses & Credits

CarbonIQ incorporates or interfaces with several open-source libraries, each retained under its respective permissive license:

* **CodeCarbon:** Apache-2.0 License (telemetry and emission calculation wrapper).
* **Click:** BSD-3-Clause License (CLI framework).
* **FastAPI:** MIT License (backend API framework).
* **React:** MIT License (frontend user interface).
* **asyncpg:** Apache-2.0 License (PostgreSQL asynchronous client).
* **Cryptography (Fernet):** Apache-2.0 / BSD License (symmetric at-rest encryption).

All original notices and upstream license terms are preserved intact.
