"""
Auth routes: signup, login, me
Passwords hashed with bcrypt. Sessions via JWT bearer tokens.
"""
import os
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt

router = APIRouter()
logger = logging.getLogger(__name__)

# --- security helpers ---------------------------------------------------------

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)

SECRET_KEY = os.getenv("JWT_SECRET", "change-me-in-production-use-a-long-random-string")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


def create_access_token(user_id: int, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": str(user_id), "email": email, "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """Dependency – validates JWT and returns the user row from DB."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    from database import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, name, email, created_at FROM users WHERE id = $1", user_id
        )
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
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
        "token": token,
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
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    try:
        from database import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            existing = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1", req.email.lower()
            )
            if existing:
                raise HTTPException(status_code=409, detail="Email already registered")

            hashed = hash_password(req.password)
            user = await conn.fetchrow(
                """INSERT INTO users (name, email, password)
                   VALUES ($1, $2, $3)
                   RETURNING id, name, email, created_at""",
                req.name, req.email.lower(), hashed,
            )
        token = create_access_token(user["id"], user["email"])
        return _user_response(user, token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Signup failed")


@router.post("/auth/login")
async def login(req: LoginRequest):
    try:
        from database import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT id, name, email, password, created_at FROM users WHERE email = $1",
                req.email.lower(),
            )
        if not user or not verify_password(req.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token(user["id"], user["email"])
        return _user_response(user, token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


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
