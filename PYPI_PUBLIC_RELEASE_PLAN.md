# CarbonIQ SDK v0.2.0 — Public PyPI Release Plan & Security Dossier

**Target Package:** `carboniq-sdk`  
**Version:** `0.2.0`  
**Repository (Release Target):** [https://github.com/Kingslaye-varun/CarbonIQ_Capstone](https://github.com/Kingslaye-varun/CarbonIQ_Capstone)  
**Upstream Team Repository:** [https://github.com/Atharvasp333/CarbonIQ](https://github.com/Atharvasp333/CarbonIQ)  
**Release Branch:** `feature/pypi-release`  
**Executable Script:** `carboniq`  
**Current Date:** November 21, 2026  
**Status:** **STAGE A (PREPARATION) COMPLETE — AWAITING STAGE B USER APPROVAL**  

---

## 1. Executive Summary & Verification State

This document certifies that the CarbonIQ Python SDK and CLI distribution (`carboniq-sdk==0.2.0`) has been completely packaged under PEP 621, isolated from the monolithic application, decoupled from local repository paths, validated against the live production backend, scanned for sensitive credentials, and configured for keyless PyPI Trusted Publishing via OpenID Connect (OIDC).

**Current Production Gate:**
- **NOTHING HAS BEEN PUBLISHED.**
- No Git tag has been pushed.
- No GitHub release has been created.
- The `main` branch and cloud deployments (Vercel & Render) remain untouched.

---

## 2. Package Identity & Metadata

```toml
[project]
name = "carboniq-sdk"
version = "0.2.0"
description = "CarbonIQ — Carbon-aware computing SDK, AST sustainable code generator, and CLI"
readme = "README.md"
requires-python = ">=3.9"
license = { text = "MIT" }
authors = [
    { name = "CarbonIQ Team", email = "team@carboniq.internal" }
]
dependencies = [
    "click>=8.1.0",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
hardware = [
    "codecarbon>=2.8.0",
]

[project.scripts]
carboniq = "carboniq.cli.carboniq_cli:cli"
```

- **Distribution Name:** `carboniq-sdk` (Available on PyPI, HTTP 404 verified).
- **Import Namespace:** `carboniq` (`import carboniq`).
- **CLI Executable:** `carboniq` (`carboniq --help`).
- **Supported Python Versions:** 3.9, 3.10, 3.11, 3.12, 3.13.
- **Platforms:** Linux, macOS, Windows (pure Python `py3-none-any`).

---

## 3. Distribution Artifacts & Cryptographic Checksums

Freshly compiled from clean, audited source tree:

| Artifact File | Distribution Type | SHA-256 Cryptographic Checksum | Size |
| :--- | :--- | :--- | :--- |
| `carboniq_sdk-0.2.0-py3-none-any.whl` | Wheel (`bdist_wheel`) | `5f1404e7ab11091bc2a58c185b4b2cf10107bd02e137814dc90a6c7364399a86` | ~27 KB |
| `carboniq_sdk-0.2.0.tar.gz` | Source Dist (`sdist`) | `c09c0d25cefd3a92d211d93af5d70b4416a48fd302ba68bf8e720414d491d7b5` | ~45 KB |

**Audit Status:**
- `twine check --strict dist/*` returned **PASSED**.
- In-archive secret scan: 0 private keys, 0 AWS access keys, 0 API tokens, 0 `.env` files.
- Prohibited paths: 0 backend files, 0 frontend files, 0 local measurement records.

---

## 4. Public Python API Validation

Tested in an isolated virtual environment outside the repository:

```python
import carboniq

# 1. Version Check
assert carboniq.__version__ == "0.2.0"

# 2. Static Code Auditing (AST)
audit = carboniq.audit_code("my_script.py")
# Returns: {'rating': 'A'|'B'|'C'|'D'|'F', 'efficiency_score': 0..100, 'issues': [...]}

# 3. Sustainable Codegen
green_code = carboniq.optimize_code("my_script.py")
# Returns: refactored string with vectorization, memoization, or streaming generators

# 4. Workload Emission Tracking
@carboniq.track(workload_name="train_model", workload_type="ml")
def run_job():
    ...

with carboniq.track("data_pipeline"):
    ...

# 5. Grid Carbon Intensity Query & Execution Deferral
intensity = carboniq.get_grid_intensity("us-east-1")
# Returns: {'aws_region': 'us-east-1', 'carbon_intensity': 395.0, ...}

@carboniq.defer_until_green(region="us-east-1", max_intensity=250.0)
def compute_intensive_task():
    ...
```

All 6 functions exist, conform to documented interfaces, and require zero hardcoded credentials.

---

## 5. CLI Command Validation Suite

The installed `carboniq` binary was verified across all 17 commands:

1. `carboniq --help` — Displays all subcommands cleanly.
2. `carboniq audit <file.py>` — AST analysis with Grade A–F score.
3. `carboniq optimize <file.py>` — Generates green code preview with vectorization blueprints.
4. `carboniq measure <command>` — Runs command and records duration, energy, emissions with transparent fallback attribution.
5. `carboniq measure-script <file.py>` — Profiles standalone Python scripts.
6. `carboniq monitor -r <region>` — Streams real-time regional grid intensity.
7. `carboniq recommend-schedule` — Validates duration and cloud region parameters.
8. `carboniq deploy-analysis` — Validates multi-step CodeCarbon + Carbon Aware SDK + AI agent analysis.
9. `carboniq carbon-intensity` — Compares real-time grid intensity across AWS regions.
10. `carboniq compare <f1> <f2>` — Diffs two measurement telemetry files.
11. `carboniq config set-key <key>` — Saves API key in `~/.carboniq/config.json`.
12. `carboniq config set-url <url>` — Saves custom backend URL.
13. `carboniq config show` — Displays active URL and masked API key.
14. `carboniq whoami` — Validates authentication and displays telemetry totals from live backend.
15. `carboniq test-backend` — Health check against `/api/health`.
16. `carboniq test-electricity-maps` — Diagnostic connectivity test for Electricity Maps.
17. `carboniq history` & `stats` — Query local and remote workload runs.

**Namespace Isolation:**
Tested `importlib.util.find_spec('cli')` -> `None`. The wheel installs **only** under `site-packages/carboniq/`, eliminating generic `cli` namespace collisions.

---

## 6. GitHub Actions Trusted Publishing Workflow

File created at `.github/workflows/release.yml`:

```yaml
name: Release CarbonIQ SDK to PyPI

on:
  release:
    types: [published]

permissions:
  contents: read

jobs:
  validate-and-build:
    name: Validate, Test, and Build Distributions
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
        with:
          fetch-depth: 1

      - name: Set up Python 3.12
        uses: actions/setup-python@42375524e23c412d93fb67b49958b491fce71c38 # v5.4.0
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Validate Release Tag against pyproject.toml
        run: |
          TAG_NAME="${{ github.ref_name }}"
          CLEAN_TAG=$(echo "$TAG_NAME" | sed -E 's/^(sdk-)?v?//')
          PYPROJECT_VERSION=$(grep -E '^version = ' pyproject.toml | head -n1 | cut -d '"' -f2)

          if [ "$CLEAN_TAG" != "$PYPROJECT_VERSION" ]; then
            echo "::error::Tag version '$CLEAN_TAG' does not match pyproject.toml version '$PYPROJECT_VERSION'!"
            exit 1
          fi

      - name: Install build and validation tools
        run: |
          python -m pip install --upgrade pip
          python -m pip install build twine

      - name: Build sdist and wheel
        run: |
          python -m build

      - name: Validate package metadata and readme rendering
        run: |
          python -m twine check --strict dist/*

      - name: Scan distribution archives for prohibited files & secrets
        run: |
          python -c '
          import zipfile, sys, glob
          wheel_files = glob.glob("dist/*.whl")
          with zipfile.ZipFile(wheel_files[0], "r") as z:
              for name in z.namelist():
                  if any(bad in name.lower() for bad in [".env", "measurements/", "backend/", "frontend/"]):
                      print(f"SECURITY VIOLATION: {name}"); sys.exit(1)
                  content = z.read(name).decode("utf-8", errors="ignore")
                  if "BEGIN RSA" in content or "BEGIN OPENSSH" in content:
                      print(f"SECURITY VIOLATION: private key in {name}"); sys.exit(1)
          print("Security check passed.")
          '

      - name: Install built wheel in isolated environment and run smoke tests
        run: |
          python -m venv test_env
          source test_env/bin/activate
          pip install dist/*.whl
          python -c "import carboniq; print('SDK loaded, version:', carboniq.__version__)"
          carboniq --help
          carboniq audit cli/sample_workloads/compute_intensive.py
          carboniq optimize cli/sample_workloads/compute_intensive.py
          python -c "import importlib.util; assert importlib.util.find_spec('cli') is None"
          deactivate
          rm -rf test_env

      - name: Upload distribution artifacts
        uses: actions/upload-artifact@4cec3d8aa04e39d1a68397de0c4cd6fb9dce8ec1 # v4.6.1
        with:
          name: pypi-artifacts
          path: dist/
          retention-days: 1

  publish-to-pypi:
    name: Publish to PyPI via Trusted Publishing (OIDC)
    needs: validate-and-build
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/carboniq-sdk
    permissions:
      id-token: write
      contents: read
    steps:
      - name: Download distribution artifacts
        uses: actions/download-artifact@cc203385981b70ca67e1cc392babf9cc229d5806 # v4.1.9
        with:
          name: pypi-artifacts
          path: dist/

      - name: Publish package distributions to PyPI
        uses: pypa/gh-action-pypi-publish@76f52bc884231f62b9a034ebfe128415bbaabdfc # release/v1.12.4
        with:
          packages-dir: dist/
          print-hash: true
```

---

## 7. Step-by-Step Pending Publisher Setup (PyPI & GitHub)

Before publishing in Stage B, configure PyPI Trusted Publishing and the GitHub protected environment:

### Step 1: Register Pending Publisher on PyPI
1. Log in to [https://pypi.org/manage/account/publishing/](https://pypi.org/manage/account/publishing/).
2. Under **"Add a GitHub publisher"**, fill in:
   - **PyPI Project Name:** `carboniq-sdk`
   - **Owner:** `Kingslaye-varun`
   - **Repository:** `CarbonIQ_Capstone`
   - **Workflow name:** `release.yml`
   - **Environment name:** `pypi`
3. Click **"Add"**. PyPI will register a pending publisher awaiting your first release run.

### Step 2: Configure Protected GitHub Environment
1. In `Kingslaye-varun/CarbonIQ_Capstone`, navigate to **Settings -> Environments**.
2. Click **"New environment"** and name it `pypi`.
3. Check **"Required reviewers"** and add yourself (`Kingslaye-varun`).
4. Under **"Deployment branches and tags"**, select **"Selected tags"** and add `v*` (or leave default).
5. Save protection rules. This ensures that even when a release is created, the job pauses until you click **Approve and deploy**.

---

## 8. Release Notes (v0.2.0)

```markdown
### CarbonIQ SDK & CLI v0.2.0 — Initial Public Release

We are excited to announce the first public release of the CarbonIQ Python SDK and CLI tool!

#### What is CarbonIQ?
CarbonIQ unites macro-level cloud infrastructure accounting with micro-level developer compute optimization.

#### Key Features:
- **AST Static Code Auditing (`carboniq audit`):** Detects CPU cycle bloat, unvectorized loops, and uncached recursion; assigns an A–F sustainability score.
- **Green Code Generator (`carboniq optimize`):** Automatically refactors algorithms using vectorization blueprints, list comprehension, and memoization.
- **Calibrated Workload Telemetry (`carboniq measure`):** Profiles arbitrary workloads with CodeCarbon hardware telemetry or an empirical 65W TDP CPU baseline fallback.
- **Carbon-Aware Decision Support (`carboniq recommend-schedule`):** Advisory ranking of low-carbon execution windows across cloud regions.
- **Grid Intensity Telemetry (`carboniq carbon-intensity`, `carboniq monitor`):** Real-time grid queries powered by Carbon Aware SDK and Electricity Maps API.
- **Authenticated Cloud Sync (`carboniq whoami`, `carboniq config`):** Synchronizes local developer telemetry with your live CarbonIQ Web Dashboard.

#### Installation:
```bash
pip install carboniq-sdk
```
For hardware RAPL/NVML profiling:
```bash
pip install "carboniq-sdk[hardware]"
```
```

---

## 9. Rollback & Yank Procedure (Emergency Defect Protocol)

If an unintended defect is discovered in a published release:
1. **Never delete a release on PyPI:** Deleting releases breaks downstream build reproducibility.
2. **Yank the defective release:**
   - Log in to PyPI -> `carboniq-sdk` -> Options -> **Yank Release**.
   - State reason: e.g. `Critical defect in CLI argument parser`.
   - Yanked releases are ignored by pip during ordinary installs but remain available to pinned builds.
3. **Issue Patch Release v0.2.1:**
   - Fix defect on `feature/pypi-release`.
   - Bump version to `0.2.1` in `pyproject.toml`, `carboniq/__init__.py`, `carboniq/cli/__init__.py`.
   - Publish v0.2.1 through the release workflow.
