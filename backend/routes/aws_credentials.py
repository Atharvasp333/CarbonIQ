"""
AWS credentials stored per user email in NeonDB.
- access_key and secret_key are encrypted with Fernet before storage.
- Decrypted transparently when retrieved for S3 operations.
- No JWT required — email comes from Neon Auth session (trusted frontend).
"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.crypto import encrypt, decrypt

router = APIRouter()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class AWSCredsRequest(BaseModel):
    email: str
    access_key: str
    secret_key: str
    region: str = "ap-south-1"
    bucket_name: str
    file_key: Optional[str] = None


class AWSCredsEmailRequest(BaseModel):
    email: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mask(key: str) -> str:
    """Show first 4 + last 4 chars only."""
    if not key or len(key) < 8:
        return "****"
    return f"{key[:4]}{'*' * (len(key) - 8)}{key[-4:]}"


async def _get_or_create_user_id(conn, email: str) -> int:
    """Get user id by email, creating the row if it doesn't exist."""
    row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email.lower())
    if row:
        return row["id"]
    row = await conn.fetchrow(
        """
        INSERT INTO users (name, email, password)
        VALUES ($1, $2, 'neon_auth_managed')
        ON CONFLICT (email) DO UPDATE SET email = EXCLUDED.email
        RETURNING id
        """,
        email.split("@")[0], email.lower()
    )
    return row["id"]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/aws/creds/save")
async def save_creds(req: AWSCredsRequest):
    """
    Encrypt and save AWS credentials for a user.
    Both access_key and secret_key are encrypted with Fernet (AES) before
    being written to NeonDB. The encryption key lives only in .env.
    """
    if not req.email:
        raise HTTPException(status_code=400, detail="email required")
    if not req.access_key or not req.secret_key:
        raise HTTPException(status_code=400, detail="access_key and secret_key required")

    # Encrypt both keys before storing
    enc_access_key = encrypt(req.access_key.strip())
    enc_secret_key = encrypt(req.secret_key.strip())

    from database import get_pool
    pool = await get_pool()
    now = datetime.now(timezone.utc)

    async with pool.acquire() as conn:
        user_id = await _get_or_create_user_id(conn, req.email)
        await conn.execute(
            """
            INSERT INTO aws_credentials
                (user_id, access_key, secret_key, region, bucket_name, file_key,
                 verified, verified_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, TRUE, $7, $7)
            ON CONFLICT (user_id) DO UPDATE
                SET access_key  = EXCLUDED.access_key,
                    secret_key  = EXCLUDED.secret_key,
                    region      = EXCLUDED.region,
                    bucket_name = EXCLUDED.bucket_name,
                    file_key    = EXCLUDED.file_key,
                    verified    = TRUE,
                    verified_at = EXCLUDED.verified_at,
                    updated_at  = EXCLUDED.updated_at
            """,
            user_id,
            enc_access_key,   # stored as "enc:gAAAAABh..."
            enc_secret_key,   # stored as "enc:gAAAAABh..."
            req.region.strip(),
            req.bucket_name.strip(),
            req.file_key.strip() if req.file_key else None,
            now,
        )

    logger.info(f"Saved encrypted AWS creds for {req.email}, bucket={req.bucket_name}")
    return {"success": True}


@router.post("/aws/creds/get")
async def get_creds(req: AWSCredsEmailRequest):
    """
    Retrieve saved credentials. Keys are decrypted before returning so the
    frontend/agent can use them directly for S3 operations.
    """
    if not req.email:
        raise HTTPException(status_code=400, detail="email required")

    from database import get_pool
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT c.access_key, c.secret_key, c.region, c.bucket_name,
                   c.file_key, c.verified, c.verified_at
            FROM aws_credentials c
            JOIN users u ON u.id = c.user_id
            WHERE u.email = $1
            """,
            req.email.lower(),
        )

    if not row:
        return {"connected": False}

    try:
        plain_access_key = decrypt(row["access_key"])
        plain_secret_key = decrypt(row["secret_key"])
    except ValueError as e:
        logger.error(f"Credential decryption failed for {req.email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to decrypt stored credentials")

    return {
        "connected": True,
        "access_key": plain_access_key,
        "secret_key": plain_secret_key,
        "access_key_masked": _mask(plain_access_key),
        "region": row["region"],
        "bucket_name": row["bucket_name"],
        "file_key": row["file_key"],
        "verified": row["verified"],
        "verified_at": row["verified_at"].isoformat() if row["verified_at"] else None,
    }


@router.post("/aws/creds/delete")
async def delete_creds(req: AWSCredsEmailRequest):
    """Remove all saved AWS credentials for a user."""
    if not req.email:
        raise HTTPException(status_code=400, detail="email required")

    from database import get_pool
    pool = await get_pool()

    async with pool.acquire() as conn:
        result = await conn.execute(
            """
            DELETE FROM aws_credentials
            WHERE user_id = (SELECT id FROM users WHERE email = $1)
            """,
            req.email.lower(),
        )

    deleted = result.split()[-1] != "0"
    logger.info(f"Deleted AWS creds for {req.email}: {deleted}")
    return {"success": True, "deleted": deleted}
