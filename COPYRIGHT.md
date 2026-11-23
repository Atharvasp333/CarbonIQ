# CarbonIQ — Copyright, Licensing & Ownership Statement

**Effective Date:** November 2026  
**Project:** CarbonIQ (Unified Cloud & Developer Carbon Intelligence Platform)  
**Distribution:** `carboniq-sdk` on PyPI  

---

## 1. Copyright Ownership Principles

The intellectual property, architecture, source code, and technical documentation of CarbonIQ are the joint creation of its four student co-founders:

* **Atharva Pingale** ([@Atharvasp333](https://github.com/Atharvasp333)) — Core Developer — Cloud & AI Architecture
* **Varun Rahatgaonkar** ([@Kingslaye-varun](https://github.com/Kingslaye-varun)) — Group 13 Team Leader, Core Developer — Python SDK, Developer Tools & Release Engineering
* **Nidhi Puthran** ([@nidhi0810](https://github.com/nidhi0810)) — Core Developer — Carbon-Aware Computing
* **Tanaya Jain** ([@tanaya2005](https://github.com/tanaya2005)) — Research, Documentation & Intellectual Property

CarbonIQ originated as the Group 13 Information Technology Capstone Project (Academic Year 2026–27) at Vivekanand Education Society's Institute of Technology (VESIT), Mumbai, under the academic guidance of Mrs. Charusheela Nehete.

### Important Ownership & IP Clarifications
1. **Repository Hosting:** Hosting the deployment fork or continuous deployment workflows at `Kingslaye-varun/CarbonIQ_Capstone` reflects operational release engineering and does not establish exclusive legal copyright over the shared codebase.
2. **PyPI Publishing:** Publishing `carboniq-sdk` to PyPI using GitHub Actions OIDC Trusted Publishing under `@Kingslaye-varun` reflects authorized distribution maintainership. It does not transfer or extinguish co-authors' copyright ownership.
3. **Software Copyright vs. Logo Intellectual Property:**
   - **Software Copyright:** Governs the computer program, algorithms, CLI, SDK, and multi-agent backend under the open-source MIT License.
   - **Logo & Design IP:** Project branding graphics, visual marks, and logo documentation represent distinct design assets. Preparatory copyright documentation was undertaken by Tanaya Jain. Any future trademark or logo copyright registration remains distinct from open-source software code licensing.
4. **No External Corporate Assignment:** The project has not been assigned, licensed exclusively, or transferred to any corporation or external commercial sponsor.
5. **Team Leader Role & Copyright Ownership:** Varun Rahatgaonkar's designation as Group 13 Team Leader reflects academic project coordination and distribution stewardship. Under open-source copyright principles, team leadership does not constitute exclusive legal copyright ownership over the collaborative codebase.

---

## 2. Personal Contribution Verification & Acknowledgment

As verified against the Git commit history, pull request audit, and project records:

> **"Varun Rahatgaonkar (@Kingslaye-varun) — CarbonIQ SDK release engineering, packaging, deployment integration, CI/CD, and developer tooling contributions."**

*Verified Scope of Work:*
* Spearheaded PEP 517/518/621 packaging for `carboniq-sdk` and configured GitHub Actions OIDC Trusted Publishing.
* Designed and implemented the AST Sustainable Code Optimizer engine (`carboniq/optimizer.py`, `carboniq audit`, `carboniq optimize`).
* Developed the CarbonIQ Visual Studio Code Extension (`vscode-extension/`).
* Engineered developer CLI features, multi-tenant user profile synchronization, and automated test suites (`tests/`).
* Configured and verified production cloud integrations on Vercel and Render.

---

## 3. Project Licensing Recommendation & Analysis

### Current Status
* `pyproject.toml` in version 0.2.0 declares `license = { text = "MIT" }` with Trove classifier `License :: OSI Approved :: MIT License`.
* The published `carboniq-sdk==0.2.0` wheel and source archive on PyPI carry this MIT declaration.
* To provide complete transparency and avoid license ambiguity, the repository operates under the **MIT License** attributed to **The CarbonIQ Authors and Contributors** (see root [`LICENSE`](LICENSE) file):

```
Copyright (c) 2026 The CarbonIQ Authors and Contributors
```

* **Contributor Approval Status:** The collective copyright notice is prepared in alignment with the MIT license declaration in `pyproject.toml` (v0.2.0). Formal written confirmation from each individual student co-founder (Atharva Pingale, Varun Rahatgaonkar, Nidhi Puthran, and Tanaya Jain) is recorded as awaiting final sign-off prior to upstream merge.

### License Options for Future Releases (v0.3.0+)

| License | Advantages | Considerations | Recommendation |
|---|---|---|---|
| **MIT License** *(Current)* | Maximum adoption, extremely permissive, standard across Python developer tools, matches v0.2.0 PyPI metadata. | Does not include an explicit patent grant or trademark clause. | **Recommended for retention** to preserve continuity with published v0.2.0 artifacts. |
| **Apache-2.0** | Permissive, includes explicit patent license and retaliation provisions; strong for cloud/enterprise tools. | Slightly more complex notices; changing from MIT to Apache-2.0 requires unanimous consent from all 4 co-authors and a new PyPI release (v0.3.0). | Strong candidate for v0.3.0+ if formal patent protection is desired. |
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
