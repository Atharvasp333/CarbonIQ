"""
Auth routes: signup, login, me
- Neon Auth JWTs (EdDSA/Ed25519) verified via PyJWT + JWKS
- Legacy HS256 tokens (our own) verified via python-jose
"""
import os
import logging
from datetime import datetime, timedelta, timezone

import httpx
import bcrypt
import jwt as pyjwt                          # PyJWT — supports EdDSA
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError, jwt as jose_jwt  # python-jose — for legacy HS256

router = APIRouter()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

bearer_scheme = HTTPBearer(auto_error=False)

NEON_AUTH_URL = os.getenv("NEON_AUTH_URL", "")
SECRET_KEY = os.getenv("JWT_SECRET", "change-me-in-production")
ALGORITHM_HS = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

# ---------------------------------------------------------------------------
# JWKS cache — PyJWT's JWKSClient handles caching + auto-refresh
# ---------------------------------------------------------------------------

_jwks_client: pyjwt.PyJWKClient | None = None


def _get_jwks_client() -> pyjwt.PyJWKClient | None:
    global _jwks_client
    if _jwks_client is None and NEON_AUTH_URL:
        jwks_url = f"{NEON_AUTH_URL.rstrip('/')}/.well-known/jwks.json"
        _jwks_client = pyjwt.PyJWKClient(jwks_url, cache_keys=True)
        logger.info(f"JWKS client initialised: {jwks_url}")
    return _jwks_client


async def _verify_neon_jwt(token: str) -> dict:
    """Verify a Neon Auth JWT (EdDSA/Ed25519) using PyJWT + JWKS."""
    client = _get_jwks_client()
    if not client:
        raise ValueError("NEON_AUTH_URL not configured")

    from urllib.parse import urlparse
    issuer = "{0.scheme}://{0.netloc}".format(urlparse(NEON_AUTH_URL))

    signing_key = client.get_signing_key_from_jwt(token)
    payload = pyjwt.decode(
        token,
        signing_key.key,
        algorithms=["EdDSA", "RS256", "ES256"],
        issuer=issuer,
        options={"verify_aud": False},
    )
    return payload


# --- password helpers --------------------------------------------------------

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash"""
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def create_access_token(user_id: int, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jose_jwt.encode(
        {"sub": str(user_id), "email": email, "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM_HS,
    )


# --- auth dependency ---------------------------------------------------------

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """
    Validates bearer token.
    1. Try Neon Auth EdDSA JWT via PyJWT + JWKS
    2. Fall back to our legacy HS256 JWT
    Auto-creates user row on first Neon Auth login.
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = credentials.credentials
    email = None

    # 1. Try Neon Auth JWT (EdDSA)
    try:
        payload = await _verify_neon_jwt(token)
        email = payload.get("email")
    except Exception as e:
        logger.debug(f"Neon JWT verify failed: {e}")

    # 2. Fall back to our own HS256 JWT
    if not email:
        try:
            payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM_HS])
            email = payload.get("email")
        except JWTError:
            pass

    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    from database import get_pool
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, name, email, created_at FROM users WHERE email = $1", email
        )

    if not user:
        # First Neon Auth login — auto-provision user row
        try:
            async with pool.acquire() as conn:
                user = await conn.fetchrow(
                    """INSERT INTO users (name, email, password)
                       VALUES ($1, $2, 'neon_auth_managed')
                       RETURNING id, name, email, created_at""",
                    email.split("@")[0], email,
                )
        except Exception as e:
            logger.error(f"Auto-create user failed: {e}")
            raise HTTPException(status_code=401, detail="Could not provision user")

    return user


# --- request / response models -----------------------------------------------

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def _user_response(user, token: str):
    return {
        "success": True,
        "access_token": token,  # Frontend expects access_token
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "createdAt": user["created_at"].isoformat(),
        },
    }


# --- endpoints ----------------------------------------------------------------

@router.post("/auth/signup")
async def signup(req: SignupRequest):
    print("=" * 80)
    print(f"SIGNUP ATTEMPT: email={req.email}, name={req.name}")
    print("=" * 80)
    
    if len(req.password) < 6:
        print("ERROR: Password too short")
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    try:
        print("Step 1: Getting database pool...")
        from database import get_pool
        pool = await get_pool()
        print(f"Step 2: Pool acquired: {pool is not None}")
        if pool is None:
            raise HTTPException(status_code=503, detail="Database unavailable")

        async with pool.acquire() as conn:
            print(f"Step 3: Checking if email exists: {req.email.lower()}")
            existing = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1", req.email.lower()
            )
            print(f"Step 4: Existing user found: {existing is not None}")
            
            if existing:
                print("ERROR: Email already registered")
                raise HTTPException(status_code=409, detail="Email already registered")

            print("Step 5: Hashing password...")
            hashed = hash_password(req.password)
            print(f"Step 6: Password hashed successfully (length={len(hashed)})")
            
            print("Step 7: Inserting user into database...")
            user = await conn.fetchrow(
                """INSERT INTO users (name, email, password)
                   VALUES ($1, $2, $3)
                   RETURNING id, name, email, created_at""",
                req.name, req.email.lower(), hashed,
            )
            print(f"Step 8: User created with ID: {user['id']}")
        
        print("Step 9: Creating JWT token...")
        token = create_access_token(user["id"], user["email"])
        print("Step 10: Token created successfully")
        print("=" * 80)
        print("SIGNUP SUCCESS")
        print("=" * 80)
        return _user_response(user, token)
    except HTTPException as he:
        print(f"HTTP EXCEPTION in signup: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        print("=" * 80)
        print(f"FATAL ERROR in signup: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        print("=" * 80)
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


@router.post("/auth/login")
async def login(req: LoginRequest):
    print("=" * 80)
    print(f"LOGIN ATTEMPT: email={req.email}")
    print("=" * 80)
    
    try:
        print("Step 1: Getting database pool...")
        from database import get_pool
        pool = await get_pool()
        print(f"Step 2: Pool acquired: {pool is not None}")
        if pool is None:
            raise HTTPException(status_code=503, detail="Database unavailable")

        async with pool.acquire() as conn:
            print(f"Step 3: Fetching user with email: {req.email.lower()}")
            user = await conn.fetchrow(
                "SELECT id, name, email, password, created_at FROM users WHERE email = $1",
                req.email.lower(),
            )
            print(f"Step 4: User found: {user is not None}")
            
        if not user:
            print("ERROR: User not found")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Handle different password formats
        stored_password = user["password"]
        print(f"Step 5: Stored password format: {stored_password[:20]}..." if len(stored_password) > 20 else f"Step 5: Stored password: {stored_password}")
        
        # If password is "neon_auth_managed", create new hash
        if stored_password == "neon_auth_managed":
            print("Step 6: Password is neon_auth_managed, creating new hash...")
            hashed = hash_password(req.password)
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET password = $1 WHERE id = $2",
                    hashed, user["id"]
                )
            print("Step 7: Password updated successfully")
        else:
            print("Step 6: Verifying password hash...")
            if not verify_password(req.password, stored_password):
                print("ERROR: Password verification failed")
                raise HTTPException(status_code=401, detail="Invalid email or password")
            print("Step 7: Password verified successfully")

        print("Step 8: Creating JWT token...")
        token = create_access_token(user["id"], user["email"])
        print("Step 9: Token created successfully")
        print("=" * 80)
        print("LOGIN SUCCESS")
        print("=" * 80)
        return _user_response(user, token)
    except HTTPException as he:
        print(f"HTTP EXCEPTION in login: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        print("=" * 80)
        print(f"FATAL ERROR in login: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        print("=" * 80)
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.get("/auth/me")
async def me(current_user=Depends(get_current_user)):
    """Return the currently authenticated user (validates token)."""
    return {
        "success": True,
        "user": {
            "id": current_user["id"],
            "name": current_user["name"],
            "email": current_user["email"],
            "createdAt": current_user["created_at"].isoformat(),
        },
    }


@router.post("/auth/sync")
async def sync_user(request: Request):
    """
    Called from frontend after Neon Auth login/signup.
    Creates or updates the user row in our users table.
    No JWT needed — trusts the payload from Neon Auth session.
    """
    body = await request.json()
    email = body.get("email", "").lower().strip()
    name = body.get("name") or email.split("@")[0]

    if not email:
        raise HTTPException(status_code=400, detail="email required")

    from database import get_pool
    pool = await get_pool()
    
    if pool is None:
        # Database unavailable - return success without persistence
        return {
            "success": True,
            "user": {
                "id": "temp-" + email,
                "name": name,
                "email": email,
                "createdAt": "2024-01-01T00:00:00",
            },
            "db_unavailable": True
        }
    
    async with pool.acquire() as conn:
        user = await conn.fetchrow("""
            INSERT INTO users (name, email, password)
            VALUES ($1, $2, 'neon_auth_managed')
            ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
            RETURNING id, name, email, created_at
        """, name, email)

    return {
        "success": True,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "createdAt": user["created_at"].isoformat(),
        },
    }


@router.get("/auth/debug-token")
async def debug_token(request: Request):
    """Debug endpoint — shows what token the backend receives."""
    auth_header = request.headers.get("authorization", "MISSING")
    if auth_header == "MISSING":
        return {"received": "no Authorization header"}
    token = auth_header.replace("Bearer ", "").replace("bearer ", "")
    try:
        import base64, json as _json
        parts = token.split(".")
        pad = lambda s: s + "=" * (-len(s) % 4)
        header = _json.loads(base64.urlsafe_b64decode(pad(parts[0])))
        payload = _json.loads(base64.urlsafe_b64decode(pad(parts[1])))
        return {"received": "token present", "header": header,
                "email": payload.get("email"), "iss": payload.get("iss")}
    except Exception as e:
        return {"received": "token present but undecipherable", "error": str(e)}
