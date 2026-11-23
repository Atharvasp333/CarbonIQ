# Changelog

All notable changes to the CarbonIQ platform, SDK, and CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2026-11-23

**Official First Public PyPI Release** of `carboniq-sdk`. Published via GitHub Actions OIDC Trusted Publishing.

### Added
* **Python SDK (`carboniq`):**
  * `carboniq.track`: Context manager and decorator for workload energy and emissions measurement.
  * `carboniq.defer_until_green`: Carbon-aware execution scheduling client.
  * `carboniq.audit_code`: Static AST carbon efficiency analysis returning an A–F rating score.
  * `carboniq.optimize_code`: Automated green code refactoring engine (memoization, vectorization, list comprehension).
* **Developer CLI (`carboniq`):**
  * `carboniq audit <path>`: Static AST sustainable code auditing with line-level anti-pattern detection.
  * `carboniq optimize <path>`: Automatic green code refactoring generator with preview and in-place options.
  * `carboniq measure <command>`: Workload profiling using CodeCarbon telemetry or calibrated 65W TDP CPU/RAM energy estimation fallback.
  * `carboniq compare`: Side-by-side execution comparison between baseline and optimized scripts.
  * `carboniq recommend-schedule`: Multi-region carbon intensity ranking and optimal scheduling guidance.
  * `carboniq deploy-analysis`: End-to-end workload measurement coupled with GSF Carbon Aware SDK regional forecasting.
  * `carboniq carbon-intensity`: Real-time regional grid intensity lookup.
  * `carboniq monitor`: Continuous real-time regional carbon intensity stream.
  * `carboniq config`: Configuration management for API keys and endpoint settings.
* **Packaging & CI/CD:**
  * PEP 517/518/621 compliant `pyproject.toml` distribution packaging.
  * Hardened GitHub Actions release workflow with exact 40-character commit SHA enforcement via `AUDITED_RELEASE_SHA`.
  * OpenID Connect (OIDC) Trusted Publishing to public PyPI with zero stored credentials.
  * Isolated test environment and complete 36-test automated verification suite.
* **Cloud Platform:**
  * Multi-agent AWS Cost and Usage Report (CUR) six-stage carbon accounting pipeline.
  * User personalization and persistent CLI workload measurement telemetry sync.
  * Executive sustainability PDF export with client-side vector rendering.

### Fixed
* Resolved generic top-level `cli` namespace collision in package distribution to preserve clean installation isolation.
* Replaced deprecated `datetime.utcnow()` with timezone-aware `datetime.now(timezone.utc)` across CLI modules.
* Enriched user authentication state with fallback organization profile data.

---

## [0.1.0] - 2026-10-24

### Added
* Initial prototype of multi-agent AWS CUR accounting engine.
* Early FastAPI backend routers for CSV upload and S3 auto-fetch.
* Initial React dashboard with service-level emissions aggregation.
* Preliminary CodeCarbon workload tracking scripts.

---

## [Unreleased] (Planned for v0.3.0+)
* Visual Studio Code Marketplace publication for the CarbonIQ IDE extension.
* Multi-cloud billing report ingestion for Google Cloud Platform (GCP BigQuery exports) and Microsoft Azure Cost Management.
* Extended emission calculation factors for managed messaging (SNS/SQS) and API Gateway.
* Webhook integrations for CI/CD green gates in GitHub Actions and GitLab CI.
