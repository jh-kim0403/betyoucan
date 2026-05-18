from ..config import settings
from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from jose import jwt, JWTError, ExpiredSignatureError
from uuid import UUID
from sqlalchemy.orm import Session
import secrets
import hashlib
from ..models.auth_schemas import RefreshToken

oauth2_scheme = OAuth2PasswordBearer("/api/v1/auth/manual/login")


def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    data = {"sub": user_id, "type": "access", "exp": expire}
    return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)
    
def generate_refresh_token():
    refresh_token_raw = secrets.token_urlsafe(64)
    return refresh_token_raw

def hash_refresh_token(token: str):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def create_refresh_token(db: Session, user_id: str) -> str:
    new_refresh_token = generate_refresh_token()
    hashed_refresh_token = hash_refresh_token(new_refresh_token)
    db_refresh_token = RefreshToken(
        user_id=user_id,
        token=hashed_refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    )
    db.add(db_refresh_token)
    db.commit()
    return new_refresh_token


def validate_access_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token,
                             settings.secret_key,
                             algorithms=["HS256"]
        )  #jose.jwt will check if it is expired. verify_exp: False will not automatically check
        user_id = UUID(payload.get("sub"))
        return user_id

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")