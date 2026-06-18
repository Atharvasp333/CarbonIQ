"""
AWS Credentials routes — save, fetch (masked), delete, auto-sync.
All endpoints require a valid JWT (get_current_user dependency).
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from routes.auth import get_current_user
from services.s3_fetcher import fetch_csv_from_s3

router = APIRouter()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class AWSCredentialsRequest(BaseModel):
    access_key: str
    secret_key: str
    region: str = "us-east-1"
    bucket_name: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mask_key(key: str) -> str:
    """Show first 4 + last 4 chars, mask the middle."""
    if not key or len(key) < 8:
        return "****"
    return f"{key[:4]}{'*' * (len(key) - 8)}{key[-4:]}"


async def _verify_s3_access(access_key: str, secret_key: str, region: str, bucket_name: str) -> str | None:
    """
    Try to list one object in the bucket to confirm credentials work.
    Returns None on success, error string on failure.
    """
    _, error = await fetch_csv_from_s3(
        access_key=access_key,
        secret_key=secret_key,
        region=region,
        bucket_name=bucket_name,
        file_key=None,          # just discovery, don't download
        verify_only=True,
    )
    return error


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/aws/credentials")
async def save_credentials(req: AWSCredentialsRequest, current_user=Depends(get_current_user)):
    """
    Save (or update) the user's AWS S3 credentials after verifying access.
    Secret key is stored as-is — Neon encrypts at rest.
    """
    user_id = current_user["id"]

    # Verify access before saving
    error = await _verify_s3_access(req.access_key, req.secret_key, req.region, req.bucket_name)
    if error:
        raise HTTPException(status_code=400, detail=f"Could not connect to S3: {error}")

    from database import get_pool
    pool = await get_pool()
    now = datetime.now(timezone.utc)

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO aws_credentials (user_id, access_key, secret_key, region, bucket_name, verified, verified_at, updated_at)
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

    logger.info(f"Saved AWS credentials for user {user_id}, bucket={req.bucket_name}")
    return {"success": True, "message": "AWS credentials saved and verified"}


@router.get("/aws/credentials")
async def get_credentials(current_user=Depends(get_current_user)):
    """Return saved credentials for the user (keys masked)."""
    user_id = current_user["id"]
    from database import get_pool
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT access_key, region, bucket_name, verified, verified_at FROM aws_credentials WHERE user_id = $1",
            user_id,
        )

    if not row:
        return {"connected": False}

    return {
        "connected": True,
        "access_key_masked": _mask_key(row["access_key"]),
        "region": row["region"],
        "bucket_name": row["bucket_name"],
        "verified": row["verified"],
        "verified_at": row["verified_at"].isoformat() if row["verified_at"] else None,
    }


@router.delete("/aws/credentials")
async def delete_credentials(current_user=Depends(get_current_user)):
    """Remove the user's saved AWS credentials."""
    user_id = current_user["id"]
    from database import get_pool
    pool = await get_pool()

    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM aws_credentials WHERE user_id = $1", user_id
        )

    deleted = result.split()[-1] != "0"
    return {"success": True, "deleted": deleted}


@router.post("/aws/auto-sync")
async def auto_sync(current_user=Depends(get_current_user)):
    """
    Fetch the latest CUR CSV from the user's saved S3 bucket and run the
    multi-agent pipeline. Returns the full analysis result.
    """
    user_id = current_user["id"]
    from database import get_pool
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT access_key, secret_key, region, bucket_name FROM aws_credentials WHERE user_id = $1 AND verified = TRUE",
            user_id,
        )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="No verified AWS credentials found. Please connect your AWS account first."
        )

    # Fetch latest CSV from S3
    csv_content, error = await fetch_csv_from_s3(
        access_key=row["access_key"],
        secret_key=row["secret_key"],
        region=row["region"],
        bucket_name=row["bucket_name"],
        file_key=None,
    )

    if error:
        raise HTTPException(status_code=400, detail=f"S3 fetch failed: {error}")

    # Run multi-agent pipeline
    try:
        from agents.orchestrator import CarbonIQOrchestrator
        orchestrator = CarbonIQOrchestrator()
        result = await orchestrator.process_cur_data(csv_content, filename=f"auto-sync:{row['bucket_name']}")
        return result
    except Exception as e:
        logger.error(f"Auto-sync pipeline error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
