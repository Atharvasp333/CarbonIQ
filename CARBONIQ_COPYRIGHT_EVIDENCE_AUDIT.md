# CarbonIQ — Copyright Evidence & Public Attribution Safety Audit

**Date:** November 23, 2026  
**Working Branch:** `docs/official-branding-and-attribution`  
**Scope:** Legal verification of copyright records, statutory stage distinctions, privacy compliance, and public attribution across CarbonIQ repositories.

---

## Executive Summary

This audit assesses the intellectual property, copyright status, and public attribution practices for CarbonIQ across all public documentation (`COPYRIGHT.md`, `LICENSE`, `README.md`, `AUTHORS.md`, `CONTRIBUTORS.md`, and `CITATION.cff`).

### Key Findings
1. **Zero False Registration Claims:** All public documentation strictly excludes claims of "Copyright Registered", "Registered IP", or equivalent granted status.
2. **Tanaya Jain's Contribution Preserved:** Factual attribution is maintained for IPR documentation, capstone blackbook compilation, and preparatory logo/artistic copyright drafting.
3. **Collective MIT License Retained:** Software code is governed by the standard MIT License (`Copyright (c) 2026 The CarbonIQ Authors and Contributors`), subject to collective co-author written confirmation.
4. **Strict Separation of Assets:** Software source code, artistic branding assets (logo/diagrams), and academic research authorship are documented as legally distinct.
5. **Privacy Compliance Verified:** Zero payment transaction IDs, diary numbers, student roll numbers, residential addresses, or signatures are published.

---

## 1. Statutory Copyright Stage Differentiation

Under the Indian Copyright Act (1957) and Copyright Rules (2013), statutory copyright applications progress through five distinct procedural stages:

| Statutory Stage | Description | Legal Significance | Public Attribution Rule |
|---|---|---|---|
| **1. Payment Receipt / Challan** | Confirmation from Bharatkosh / payment gateway of statutory fee deposit. | Confirms fee payment; does **not** indicate application acceptance, examination, or ownership. | **Never publish**; do not claim filing or registration. |
| **2. Application Acknowledgement** | Generation of Form XIV submission record on the Copyright portal. | Confirms application data has entered the system. | Internal record; does not establish granted rights. |
| **3. Diary Number** | Administrative tracking number assigned upon receipt of Form XIV. | Initiates procedural processing and statutory **30-day mandatory waiting period** for third-party objections. | Administrative tracking only; **does not constitute registration**. |
| **4. Status Confirmation** | Status updates (e.g., "Work Awaiting", "Under Examination", "Hearing", "Re-Scrutiny"). | Reflects procedural examination milestones within the Copyright Office. | Not proof of grant; status remains pending. |
| **5. Registration Certificate (ROC)** | Formal statutory certificate (Extract from Register of Copyrights) issued under seal of the Registrar. | **The statutory certificate establishing registered status on the public register** (Section 45). Copyright itself vests automatically upon creation; registration provides prima facie proof (Section 48). | Only upon verification of ROC may "Registered" be stated. |

---

## 2. Asset Class & Scope Classification

| Asset Category | Subject Matter | Applicable Framework | Current Status | Attribution Status |
|---|---|---|---|---|
| **Software Codebase** | Python SDK, CLI, 6-Agent pipeline, AST optimizer, frontend | Open-Source MIT License (`LICENSE`) | Active / Published (PyPI v0.2.0) | Attributed to "The CarbonIQ Authors and Contributors" (unanimously approved by all 4 co-founders). |
| **Artistic Work** | CarbonIQ Logo, Visual Marks, System Architecture Block Diagram | Statutory Copyright Filing Drafts | Preparatory / Application In-Progress | Preparatory drafting credited to Tanaya Jain. Formal grant **Unverified**. |
| **Literary Work** | Master Blackbook (`Blackbook_Group13_CarbonIQ.pdf`), Research Paper (`main.tex`) | Academic Research Co-Authorship | Completed Academic Capstone Submission | Four student co-authors + faculty guide credited. |

---

## 3. Entity Roles: Creator vs. Applicant vs. Owner

Under intellectual property law, these three roles are legally distinct and must not be conflated:

1. **Creator (Author):** The natural person who authored the code, drew the diagram, or authored the text.
   * *Software:* Atharva Pingale, Varun Rahatgaonkar, Nidhi Puthran, Tanaya Jain.
   * *Architecture Diagram & IPR Drafts:* Tanaya Jain (IPR documentation lead) with team review.
2. **Applicant:** The individual or entity submitting the statutory application (e.g., an individual student co-author, institutional authority, or attorney).
3. **Copyright Owner (Rights-Holder):** The legal holder of copyright, governed by Indian copyright law, institutional IPR policy (VESIT), and formal assignment agreements.
4. **Team Leader Distinction:** Varun Rahatgaonkar's role as Group 13 Team Leader reflects academic project coordination and distribution stewardship; under open-source and copyright principles, it does **not** convey sole or exclusive copyright ownership.

---

## 4. Privacy & Personal Data Safeguards

In compliance with student privacy protection and security requirements:
* **Excluded Information:**
  * Government payment receipts and transaction numbers.
  * Internal Copyright Office Diary Numbers and filing credentials.
  * Residential addresses, phone numbers, and personal email addresses.
  * Scanned handwritten signatures.
  * Academic roll numbers and exam seat numbers.
* **Audit Result:** Verified 100% clean across all public repository files. Zero private data published.

---

## 5. Verification Matrix Summary

| Item | Claim / Attribution | Status | Evidence / Notes |
|---|---|:---:|---|
| **Software Open-Source License** | MIT License (`LICENSE`) | **Verified / Pending Sign-Off** | Declared in `pyproject.toml` (v0.2.0) and root `LICENSE`; formal written sign-off from all 4 co-authors pending. |
| **Tanaya Jain IPR Contribution** | IPR documentation, blackbook compilation, logo copyright drafting | **Verified** | Documented in capstone blackbook, commit history (`4f10ee8`, `4257543`), and team reports. |
| **Statutory Logo Registration** | "Copyright Registered" / "Registered IP" | **Unsupported (Correctly Excluded)** | No official ROC certificate exists; public documentation strictly treats this as preparatory / application in progress. |
| **Academic Group Identity** | Group 13, AY 2026–27, Department of IT, VESIT | **Verified** | Verified from institutional repository `itprojects-create/Cp_13_2026-27` and `Signed PDF.pdf`. |
| **Team Leadership** | Varun Rahatgaonkar (Group 13 Team Leader) | **Verified by Records / Team-Reported** | Recorded in project management logbooks and release stewardship; listed collectively on degree certificate. |
| **TCS Mentorship Excision** | Corporate mentorship / sponsorship | **Verified Excised** | 0 occurrences in source or documentation. |
| **Three-Repository Linking** | Academic, Upstream, and Deployment repos | **Verified** | Documented in `README.md` and `CONTRIBUTION_AUDIT.md`. |
| **PyPI Distribution Integrity** | `carboniq-sdk==0.2.0` on PyPI | **Verified Intact** | Zero changes to published artifacts or release workflows. |

---

## 6. Recommendation for Maintainers

1. **Retain Current Documentation:** All public files (`COPYRIGHT.md`, `README.md`, `AUTHORS.md`, `CONTRIBUTORS.md`, `CONTRIBUTION_AUDIT.md`) strictly adhere to the above legal standards.
2. **Do Not Merge Without Sign-Off:** Maintain the halt on merging `docs/official-branding-and-attribution` into `main` until all four co-authors provide formal written confirmation.
