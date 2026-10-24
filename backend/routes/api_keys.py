"""
API Keys Management Routes
Provides secure API key generation, validation, and listing for CLI & SDK users.
"""
import secrets
import hashlib
import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request, Header
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel

from database import get_pool
from routes.auth import get_current_user, bearer_scheme, _verify_neon_jwt, jose_jwt, SECRET_KEY, ALGORITHM_HS, JWTError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/user/api-keys", tags=["api-keys"])


def hash_api_key(raw_key: str) -> str:
    """Hash an API key using SHA-256 for secure storage"""
    return hashlib.sha256(raw_key.strip().encode('utf-8')).hexdigest()


def generate_new_key(name: str = "Default CLI Key") -> tuple[str, str, str]:
    """
    Generate a new API key with ciq_live_ prefix
    Returns (raw_key, key_prefix, key_hash)
    """
    token = secrets.token_hex(20)
    raw_key = f"ciq_live_{token}"
    prefix = f"{raw_key[:12]}..."
    key_hash = hash_api_key(raw_key)
    return raw_key, prefix, key_hash


async def get_user_from_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> Optional[dict]:
    """Validate X-API-Key header and return user dict, or None"""
    if not x_api_key:
        return None
    
    key_hash = hash_api_key(x_api_key)
    pool = await get_pool()
    
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT k.id as key_id, k.user_id, u.id, u.name, u.email
                FROM api_keys k
                JOIN users u ON u.id = k.user_id
                WHERE k.key_hash = $1
            """, key_hash)
            
            if row:
                # Update last_used_at in background
                await conn.execute("""
                    UPDATE api_keys SET last_used_at = NOW() WHERE id = $1
                """, row['key_id'])
                
                return {
                    "id": row['id'],
                    "name": row['name'],
                    "email": row['email']
                }
    except Exception as e:
        logger.error(f"Error checking API key: {e}")
        
    return None


async def get_current_user_or_api_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> Optional[dict]:
    """
    Resolves authenticated user from either:
    1. X-API-Key header (CLI & SDK)
    2. Bearer JWT token (Web Dashboard)
    Returns user dict or None
    """
    # 1. Try X-API-Key
    if x_api_key:
        user = await get_user_from_api_key(x_api_key)
        if user:
            return user
            
    # 2. Try Bearer JWT
    if credentials:
        token = credentials.credentials
        
        # Check if Bearer token is actually an API key (e.g. Bearer ciq_live_...)
        if token.startswith("ciq_live_"):
            user = await get_user_from_api_key(token)
            if user:
                return user
                
        # Try JWT
        email = None
        try:
            payload = await _verify_neon_jwt(token)
            email = payload.get("email")
        except Exception:
            pass
            
        if not email:
            try:
                payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM_HS])
                email = payload.get("email")
            except JWTError:
                pass
                
        if email:
            pool = await get_pool()
            async with pool.acquire() as conn:
                user = await conn.fetchrow("SELECT id, name, email FROM users WHERE email = $1", email)
                if user:
                    return dict(user)
                    
    return None


class CreateApiKeyRequest(BaseModel):
    name: Optional[str] = "CLI Key"


@router.get("")
async def list_user_api_keys(current_user = Depends(get_current_user)):
    """List all API keys for the current authenticated dashboard user"""
    user_id = current_user['id']
    pool = await get_pool()
    
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, name, key_prefix, created_at, last_used_at
                FROM api_keys
                WHERE user_id = $1
                ORDER BY created_at DESC
            """, user_id)
            
        keys = []
        for r in rows:
            keys.append({
                "id": r["id"],
                "name": r["name"],
                "key_prefix": r["key_prefix"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "last_used_at": r["last_used_at"].isoformat() if r["last_used_at"] else None,
            })
            
        return {
            "success": True,
            "keys": keys
        }
    except Exception as e:
        logger.error(f"Failed to list API keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_api_key(req: CreateApiKeyRequest, current_user = Depends(get_current_user)):
    """Generate a new API key for the current authenticated user"""
    user_id = current_user['id']
    raw_key, prefix, key_hash = generate_new_key(req.name or "CLI Key")
    pool = await get_pool()
    
    try:
        async with pool.acquire() as conn:
            key_id = await conn.fetchval("""
                INSERT INTO api_keys (user_id, key_hash, key_prefix, name)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, user_id, key_hash, prefix, req.name or "CLI Key")
            
        return {
            "success": True,
            "id": key_id,
            "name": req.name or "CLI Key",
            "api_key": raw_key,
            "prefix": prefix,
            "message": "Store this key safely! You won't be able to view the full key again."
        }
    except Exception as e:
        logger.error(f"Failed to create API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{key_id}")
async def revoke_api_key(key_id: int, current_user = Depends(get_current_user)):
    """Revoke/Delete an API key for the authenticated user"""
    user_id = current_user['id']
    pool = await get_pool()
    
    try:
        async with pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM api_keys
                WHERE id = $1 AND user_id = $2
            """, key_id, user_id)
            
        return {
            "success": True,
            "message": "API key revoked successfully"
        }
    except Exception as e:
        logger.error(f"Failed to revoke API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))
