# PyPI Publishing Guide for CarbonIQ

This guide explains how the `carboniq` Python SDK is built and published to PyPI (Python Package Index) so anyone in the world can run `pip install carboniq`.

---

## 📦 Package Distribution Files

The build process generates two standard distribution artifacts in the `dist/` directory:
1. **Source Archive (`sdist`)**: `dist/carboniq-0.2.0.tar.gz`
2. **Binary Wheel (`wheel`)**: `dist/carboniq-0.2.0-py3-none-any.whl`

Both packages have been verified with `twine check` and passed with **0 warnings**:
```bash
python -m twine check dist/*
# Checking dist\carboniq-0.2.0-py3-none-any.whl: PASSED
# Checking dist\carboniq-0.2.0.tar.gz: PASSED
```

---

## 🚀 How to Publish to PyPI

### Option A: TestPyPI (Recommended for staging first)
1. Create an account on [test.pypi.org](https://test.pypi.org) and generate an API Token (`pypi-...`).
2. Upload using Twine:
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```
3. Test installation from TestPyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ carboniq
   ```

---

### Option B: Production PyPI (`pip install carboniq`)
1. Create an account on [pypi.org](https://pypi.org) and generate an API Token (`pypi-...`).
2. Run:
   ```bash
   python -m twine upload dist/*
   ```
   * Username: `__token__`
   * Password: `pypi-your-token-here`
3. Verify global installation on any machine:
   ```bash
   pip install carboniq
   ```

---

## 🔄 Automated GitHub Actions Publishing (Optional)

You can automate publishing whenever a git release tag (`v0.2.0`) is pushed to GitHub using `.github/workflows/pypi-publish.yml` with `pypa/gh-action-pypi-publish`.
