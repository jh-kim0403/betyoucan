from fastapi import APIRouter, Depends, HTTPException, Request, status
import logging
from src.helpers.db import get_db
from src.helpers.auth_utils import hash_refresh_token, create_access_token, create_refresh_token
from sqlalchemy.orm import Session
from src.models.auth_schemas import RefreshToken, User
from src.models.auth_models import RefreshRequest, RefreshResponse
from typing import Optional
from datetime import datetime, timezone


router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

def get_refresh_token(refresh_token: str, db: Session) -> RefreshToken | None:
    refresh_token = hash_refresh_token(refresh_token)
    refresh_result = (db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first())
    return refresh_result

@router.post("/refresh", response_model=RefreshResponse)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    refresh_token = payload.refresh_token
    if not refresh_token:
        raise HTTPException(status_code=400, detail="refresh token missing")
    
    try:
        token = get_refresh_token(payload.refresh_token, db)
    except Exception:
        raise HTTPException(status_code=503, detail="Auth service unavailable")
    
    if not token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    if token.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Refresh token revoked")
    now = datetime.now(timezone.utc)
    if token.expires_at < now:
        raise HTTPException(status_code=401, detail="refresh token expired")

    user_id = str(token.user_id)
    access_token = create_access_token(user_id)
    token.revoked_at = datetime.now(timezone.utc)
    db.commit()
    new_refresh_token = create_refresh_token(db, user_id)
    identity = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )
    return RefreshResponse(
        user_id=user_id,
        email=identity.email,
        first_name=identity.first_name,
        last_name=identity.last_name,
        refresh_token=new_refresh_token,
        access_token=access_token
    )

    
