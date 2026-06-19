"""
Symmetric encryption for sensitive credentials stored in NeonDB.

Uses Fernet (AES-128-CBC + HMAC-SHA256) from the cryptography library.
Key is loaded from CREDS_ENCRYPTION_KEY in .env — never stored in DB.

Encrypted values are prefixed with "enc:" so it's obvious they're ciphertext.
Plain values (legacy) are returned as-is so old unencrypted rows still work.
"""
import os
import logging
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

_ENCRYPTED_PREFIX = "enc:"
_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = os.getenv("CREDS_ENCRYPTION_KEY", "").strip()
        if not key:
            raise RuntimeError(
                "CREDS_ENCRYPTION_KEY is not set. "
                "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        _fernet = Fernet(key.encode())
    return _fernet


def encrypt(value: str) -> str:
    """
    Encrypt a plaintext string and return a prefixed ciphertext string.
    Example: "AKIAIOSFODNN7EXAMPLE" → "enc:gAAAAABh..."
    """
    if not value:
        return value
    token = _get_fernet().encrypt(value.encode()).decode()
    return f"{_ENCRYPTED_PREFIX}{token}"


def decrypt(value: str) -> str:
    """
    Decrypt an encrypted string. If value is not prefixed (legacy plain text),
    returns it unchanged so old rows still work.
    """
    if not value:
        return value
    if not value.startswith(_ENCRYPTED_PREFIX):
        # Legacy unencrypted value — return as-is
        logger.debug("Decrypting legacy unencrypted credential value")
        return value
    token = value[len(_ENCRYPTED_PREFIX):]
    try:
        return _get_fernet().decrypt(token.encode()).decode()
    except InvalidToken:
        logger.error("Failed to decrypt credential — wrong key or corrupted data")
        raise ValueError("Could not decrypt credential. Check CREDS_ENCRYPTION_KEY.")


def is_encrypted(value: str) -> bool:
    """Check if a value is already encrypted."""
    return bool(value and value.startswith(_ENCRYPTED_PREFIX))
