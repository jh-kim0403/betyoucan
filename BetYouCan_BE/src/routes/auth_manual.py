import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
import ipaddress
import hashlib
import secrets
from typing import Optional
from passlib.hash import argon2
from ..models import auth_models, auth_schemas
from ..helpers.db import get_db
from ..helpers import auth_utils as tk
from ..helpers.email import send_verification_email
from datetime import datetime, timezone, timedelta



router = APIRouter(prefix="/api/v1/auth/manual", tags=["Manual Auth"])

def _extract_client_ip(request: Request) -> Optional[str]:
    """Return a valid IPv4/IPv6 string from headers/client or None if unavailable.
    - Prefers the first entry of X-Forwarded-For when present
    - Falls back to request.client.host
    - Validates using ipaddress; returns None if invalid (e.g., 'testclient')
    """
    # Try X-Forwarded-For (could be a list: client, proxy1, proxy2...)
    xff = request.headers.get("x-forwarded-for")
    candidate: Optional[str] = None
    if xff:
        candidate = xff.split(",")[0].strip()
    else:
        # Fall back to the direct client
        if request.client and request.client.host:
            candidate = request.client.host

    if not candidate:
        return None

    try:
        # Validate IP (raises ValueError if not a real IP)
        ipaddress.ip_address(candidate)
        return candidate
    except ValueError:
        return None

def _generate_verification_token() -> tuple[str, str]:
    """Return (raw_token, token_hash). Store the hash; email the raw token."""
    raw = secrets.token_urlsafe(32)
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


@router.post("/signup", response_model=auth_models.SignUpResponse, status_code=status.HTTP_201_CREATED)
def signup_manual(payload: auth_models.SignupManual, request: Request, db: Session = Depends(get_db)):
    payload.email = payload.email.lower().strip()
    existing = db.query(auth_schemas.User).filter(auth_schemas.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = auth_schemas.User(
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        signup_ip=_extract_client_ip(request),
        is_active=False,
    )
    db.add(user)
    db.flush()  # to get user.id

    identity = auth_schemas.AuthIdentity(
        user_id=user.id,
        provider="password",
        email=payload.email,
        password_hash=argon2.hash(payload.password),
    )
    db.add(identity)

    raw_token, token_hash = _generate_verification_token()
    verification = auth_schemas.EmailVerificationToken(
        user_id=user.id,
        token=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )

    db.add(verification)

    send_verification_email(user.email, user.first_name, raw_token)

    db.commit()

    return user
    


@router.post("/login", response_model=auth_models.LoginResponse)
def login_manual(payload: auth_models.ManualLoginRequest, response: Response, db: Session = Depends(get_db)):
    payload.email = payload.email.lower().strip()
    identity = (
            db.query(auth_schemas.AuthIdentity)
            .filter(auth_schemas.AuthIdentity.email == payload.email, auth_schemas.AuthIdentity.provider == "password")
            .first()
        )
    if not identity:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not identity.user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not active yet")
    if not argon2.verify(payload.password, identity.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if payload.timezone and identity.user.timezone != payload.timezone:
        identity.user.timezone = payload.timezone
    logging.info("login payload timezone=%s", payload.timezone)
    access_token = tk.create_access_token(str(identity.user.id))
    refresh_token = tk.create_refresh_token(db=db, user_id=identity.user.id)
    identity.user.last_login_at = datetime.now(timezone.utc)  # move here
    db.commit()

    return auth_models.LoginResponse(
        user_id=identity.user.id,
        email=identity.email,
        first_name=identity.user.first_name,
        last_name=identity.user.last_name,
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    record = (
        db.query(auth_schemas.EmailVerificationToken)
        .filter(auth_schemas.EmailVerificationToken.token == token_hash)
        .first()
    )
    if not record:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    if record.used_at is not None:
        raise HTTPException(status_code=400, detail="Token already used")
    if record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token expired")

    record.used_at = datetime.now(timezone.utc)
    record.user.email_verified = True
    record.user.is_active = True
    db.commit()
    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
def resend_verification(payload: auth_models.ResendVerificationRequest, db: Session = Depends(get_db)):
    user = db.query(auth_schemas.User).filter(auth_schemas.User.email == payload.email).first()
    # Always return 200 to avoid leaking whether an email is registered
    if not user or user.email_verified:
        return {"message": "If that email exists and is unverified, a new link has been sent"}

    raw_token, token_hash = _generate_verification_token()
    verification = auth_schemas.EmailVerificationToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db.add(verification)
    db.commit()

    send_verification_email(user.email, user.first_name, raw_token)
    return {"message": "If that email exists and is unverified, a new link has been sent"}
