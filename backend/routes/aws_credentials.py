"""
AWS credentials stored per user email — no JWT required.
Email comes from the Neon Auth session (trusted on frontend, passed in body).
"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
logger = logging.getLogger(__name__)


class AWSCredsRequest(BaseModel):
    email: str
    access_key: str
    secret_key: str
    region: str = "ap-south-1"
    bucket_name: str
    file_key: Optional[str] = None


class AWSCredsEmailRequest(BaseModel):
    email: str


async def _get_or_create_user_id(conn, email: str) -> int:
    """Get user id by email, creating the row if it doesn't exist."""
    row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email.lower())
    if row:
        return row["id"]
    row = await conn.fetchrow(
        "INSERT INTO users (name, email, password) VALUES ($1, $2, 'neon_auth_managed') "
        "ON CONFLICT (email) DO UPDATE SET email = EXCLUDED.email RETURNING id",
        email.split("@")[0], email.lower()
    )
    return row["id"]


@router.post("/aws/creds/save")
async def save_creds(req: AWSCredsRequest):
    """Save/update AWS credentials for a user (keyed by email)."""
    if not req.email:
        raise HTTPException(status_code=400, detail="email required")

    from database import get_pool
    pool = await get_pool()
    now = datetime.now(timezone.utc)

    async with pool.acquire() as conn:
        user_id = await _get_or_create_user_id(conn, req.email)
        await conn.execute("""
            INSERT INTO aws_credentials
                (user_id, access_key, secret_key, region, bucket_name, verified, verified_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, TRUE, $6, $6)
            ON CONFLICT (user_id) DO UPDATE
                SET access_key  = EXCLUDED.access_key,
                    secret_key  = EXCLUDED.secret_key,
                    region      = EXCLUDED.region,
                    bucket_name = EXCLUDED.bucket_name,
                    verified    = TRUE,
                    verified_at = EXCLUDED.verified_at,
                    updated_at  = EXCLUDED.updated_at
        """, user_id, req.access_key, req.secret_key, req.region, req.bucket_name, now)

    logger.info(f"Saved AWS creds for {req.email}, bucket={req.bucket_name}")
    return {"success": True}


@router.post("/aws/creds/get")
async def get_creds(req: AWSCredsEmailRequest):
    """Get saved AWS credentials for a user (secret key masked for display)."""
    if not req.email:
        raise HTTPException(status_code=400, detail="email required")

    from database import get_pool
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT c.access_key, c.secret_key, c.region, c.bucket_name, c.verified, c.verified_at
            FROM aws_credentials c
            JOIN users u ON u.id = c.user_id
            WHERE u.email = $1
        """, req.email.lower())

    if not row:
        return {"connected": False}

    k = row["access_key"]
    return {
        "connected": True,
        "access_key": row["access_key"],        # full key — needed for sync
        "secret_key": row["secret_key"],        # full key — needed for sync
        "access_key_masked": f"{k[:4]}{'*'*(len(k)-8)}{k[-4:]}",
        "region": row["region"],
        "bucket_name": row["bucket_name"],
        "verified": row["verified"],
        "verified_at": row["verified_at"].isoformat() if row["verified_at"] else None,
    }


@router.post("/aws/creds/delete")
async def delete_creds(req: AWSCredsEmailRequest):
    """Remove AWS credentials for a user."""
    if not req.email:
        raise HTTPException(status_code=400, detail="email required")

    from database import get_pool
    pool = await get_pool()

    async with pool.acquire() as conn:
        result = await conn.execute("""
            DELETE FROM aws_credentials
            WHERE user_id = (SELECT id FROM users WHERE email = $1)
        """, req.email.lower())

    return {"success": True, "deleted": result.split()[-1] != "0"}
