# CarbonIQ Development & Testing Guide

This guide describes how to set up CarbonIQ for local development, run automated test suites, build package distributions, and maintain high code quality.

---

## 1. Prerequisites

* **Python:** Version 3.9, 3.10, 3.11, or 3.12+ (3.12 recommended)
* **Node.js:** Version 18+ and npm (for frontend and VS Code extension development)
* **Git:** Version 2.30+

---

## 2. Environment Setup

Clone the repository and initialize a dedicated virtual environment:

```bash
git clone https://github.com/Kingslaye-varun/CarbonIQ_Capstone.git
cd CarbonIQ_Capstone

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package in editable mode with development dependencies
pip install -e .
pip install pytest twine build
```

---

## 3. Running Automated Tests

CarbonIQ includes a comprehensive test suite covering the Python SDK, CLI commands, packaging isolation, and grid integration:

```bash
# Run all automated tests
pytest tests/ -v
```

### Specific Test Modules:
```bash
# SDK public API tests
pytest tests/test_sdk_api.py -v

# CLI command tests (audit, optimize, measure, compare)
pytest tests/test_cli_commands.py -v

# Packaging, wheel isolation, and security scan tests
pytest tests/test_packaging_and_security.py -v

# Carbon Aware SDK integration and fallback tests
pytest tests/test_carbon_aware_integration.py -v
```

---

## 4. Building and Validating Package Distributions

To test the distribution build locally before submitting changes:

```bash
# Clean prior build artifacts
rm -rf dist/ build/ *.egg-info

# Build wheel and sdist
python -m build

# Strict metadata and README rendering check
python -m twine check --strict dist/*
```

### Testing Clean Wheel Isolation:
To verify that the built wheel does not leak generic namespace shims into `site-packages`:

```bash
# In a temporary directory outside the repository:
python -m venv /tmp/isolated_test_env
source /tmp/isolated_test_env/bin/activate
pip install <path-to-dist>/*.whl

# Assert import and CLI work
python -c "import carboniq; assert carboniq.__version__ == '0.2.0'"
carboniq --help
deactivate
rm -rf /tmp/isolated_test_env
```

---

## 5. Coding Standards & Git Guidelines

1. **Conventional Commits:** Write clear commit messages using the format `<type>(<scope>): <description>` (e.g., `feat(optimizer): add list comprehension transformation`, `fix(cli): handle missing config gracefully`).
2. **Type Annotations:** Use Python type hints where practical.
3. **No Secret Commits:** Ensure no credentials or live API keys are added to git.
4. **Clean PRs:** Ensure all 36 tests pass before opening a Pull Request.
