# Contributing to CarbonIQ

Thank you for your interest in contributing to CarbonIQ! We welcome contributions to our cloud accounting platform, Python SDK, developer CLI, and VS Code extension.

---

## Code of Conduct

All contributors and participants are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please treat all members of the community with respect.

---

## Repository Structure & Forking Workflow

CarbonIQ maintains two connected repositories:
- **Upstream:** [Atharvasp333/CarbonIQ](https://github.com/Atharvasp333/CarbonIQ) (Core platform and research base)
- **Deployment & PyPI Fork:** [Kingslaye-varun/CarbonIQ_Capstone](https://github.com/Kingslaye-varun/CarbonIQ_Capstone) (Packaging, CI/CD, and live releases)

### Development Process
1. Fork the appropriate repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/CarbonIQ.git
   cd CarbonIQ
   ```
3. Create a topic branch from `main`:
   ```bash
   git checkout -b feature/my-improvement
   ```
4. Commit your changes with clear, descriptive commit messages adhering to Conventional Commits:
   - `feat(...)`: New features
   - `fix(...)`: Bug fixes
   - `docs(...)`: Documentation updates
   - `test(...)`: Adding or updating tests
5. Push to your fork and submit a Pull Request targeting `main`.

---

## Local Development & Testing

### Python SDK and CLI
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with development dependencies
pip install -e .
pip install pytest twine build

# Run automated tests
pytest tests/ -v
```

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

---

## Pull Request Guidelines

1. **Test Coverage:** Ensure existing tests pass and add unit tests for new functionality.
2. **Isolation Guarantee:** Ensure the Python SDK (`carboniq`) remains clean and does not introduce top-level namespace pollution (e.g., generic `cli` packages).
3. **No Secrets:** Never commit real API keys, credentials, or `.env` files.
4. **Attribution:** New contributors will be acknowledged in [CONTRIBUTORS.md](CONTRIBUTORS.md).

For questions or larger architectural proposals, please open an Issue before submitting a large pull request.
