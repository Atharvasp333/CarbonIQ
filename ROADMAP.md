# CarbonIQ Project Roadmap

This document outlines the strategic milestones and technical roadmap for CarbonIQ across cloud accounting, developer tooling, and open-source ecosystem growth.

---

## Current Release: v0.2.0 (Completed ✅)

- [x] **Public PyPI Launch:** `pip install carboniq-sdk` live on PyPI via GitHub Actions OIDC Trusted Publishing.
- [x] **Python SDK & CLI:** `carboniq` unified package featuring AST static audit, green code generation, and carbon-aware execution.
- [x] **Cloud Multi-Agent Pipeline:** 6-agent sequential accounting engine ingesting AWS Cost and Usage Reports (CUR).
- [x] **Carbon-Aware Intelligence:** Green Software Foundation Carbon Aware SDK and Electricity Maps integration.
- [x] **Full-Stack Production Deployments:** Production web application live on Vercel and Render with NeonDB PostgreSQL.
- [x] **Rigorous Test Suite:** 36 automated unit, CLI, integration, and package isolation tests passing cleanly.

---

## Near-Term Milestone: v0.3.0 (Q1 2027)

- [ ] **VS Code Marketplace Release:** Package and publish the verified CarbonIQ VS Code extension to the official Visual Studio Marketplace.
- [ ] **Expanded Metadata & Attribution:** Formally register all four co-founders in `pyproject.toml` author metadata on PyPI.
- [ ] **Enhanced AST Refactoring:**
  - Automatic detection and refactoring of inefficient nested dictionary traversals.
  - Integration with Ruff / Flake8 plugin APIs as an AST-based green linter.
- [ ] **CI/CD GitHub Action:** Provide an official GitHub Action (`action-carboniq-audit`) to establish green PR thresholds and lint compute regressions in CI pipelines.

---

## Mid-Term Milestone: v0.4.0 (Q2 2027)

- [ ] **Multi-Cloud Ingestion:**
  - Google Cloud Platform (GCP) carbon footprint and BigQuery billing export parser.
  - Microsoft Azure Cost Management export parser.
- [ ] **Expanded Service Emission Factors:** Support for Amazon API Gateway, DynamoDB, Amazon SQS/SNS, and managed Kubernetes (EKS) clusters.
- [ ] **Enterprise Telemetry Webhooks:** Stream live CLI and cloud emissions logs to Datadog, Prometheus, or Grafana dashboards.

---

## Long-Term Vision: v1.0.0 (2027)

- [ ] **Automated Workload Deferral API:** Production-grade execution queue daemon with automated job deferral based on carbon forecast windows.
- [ ] **Consensus Multi-Agent Optimization:** Dynamic multi-agent debate architecture comparing financial cost vs carbon intensity trade-offs.
- [ ] **Community Governance:** Transition to an open community governance model with regular community meetings and an RFC process.
