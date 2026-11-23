# Security Policy

The CarbonIQ development team takes security and privacy seriously. This document describes our supported versions and vulnerability reporting process.

---

## Supported Versions

Security updates are actively maintained on the latest stable branch and PyPI package distributions:

| Distribution / Component | Supported Version | Security Status |
|---|---|---|
| `carboniq-sdk` (PyPI) | `0.2.0` | Active Security Support |
| `CarbonIQ Backend API` | `main` | Active Security Support |
| `CarbonIQ Frontend` | `main` | Active Security Support |
| Prior pre-release versions | `< 0.2.0` | End of Life (Upgrade Required) |

---

## Reporting a Vulnerability

If you discover a security vulnerability or sensitive data exposure in CarbonIQ, please report it responsibly:

1. **Do Not File Public Issues:** Please do NOT submit security reports or secret exposure reports via public GitHub issues, discussions, or pull requests.
2. **Private Reporting:** Open a **GitHub Security Advisory** privately on the repository:
   - Go to the **Security** tab of [Kingslaye-varun/CarbonIQ_Capstone](https://github.com/Kingslaye-varun/CarbonIQ_Capstone) or [Atharvasp333/CarbonIQ](https://github.com/Atharvasp333/CarbonIQ).
   - Click **Report a vulnerability**.
3. **Response Timeline:** A maintainer will acknowledge receipt of your report within 48 hours, validate the vulnerability, and coordinate a patch and advisory release.

---

## Security Practices in CarbonIQ

* **Credential Sanitization:** User credentials (such as AWS access keys) are encrypted using symmetric Fernet/AES encryption before storage.
* **No Plaintext Secrets in CI/CD:** Release automation relies exclusively on OpenID Connect (OIDC) federated identity tokens, eliminating long-lived PyPI API tokens.
* **AST Safety:** The AST optimizer evaluates code structure statically without executing untrusted user Python scripts during `carboniq audit` or `carboniq optimize`.
