from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
from ..models import auth_models, auth_schemas
from ..helpers.db import get_db
from sqlalchemy.sql import func
import os

router = APIRouter(prefix="/api/v1/auth/google", tags=["Google OAuth2"])
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID_WEB")

@router.post("/signup", response_model=auth_models.LoginResponse)
def signup_google(payload: auth_models.SignupGoogle, db: Session = Depends(get_db)):
    try:
        idinfo = id_token.verify_oauth2_token(payload.id_token, requests.Request(), GOOGLE_CLIENT_ID)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    email = idinfo.get("email")
    sub = idinfo.get("sub")
    name = idinfo.get("name")
    picture = idinfo.get("picture")
    verified = idinfo.get("email_verified", False)

    user = db.query(auth_schemas.User).filter(auth_schemas.User.email == email).first()
    if not user:
        # Split name into first and last name
        name_parts = name.split(' ', 1) if name else ['', '']
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        user = auth_schemas.User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            photo_url=picture,
            email_verified=verified,
        )
        db.add(user)
        db.flush()

    identity = (
        db.query(auth_schemas.AuthIdentity)
        .filter(auth_schemas.AuthIdentity.provider == "google", auth_schemas.AuthIdentity.provider_user_id == sub)
        .first()
    )
    
    if not identity:
        identity = auth_schemas.AuthIdentity(
            user_id=user.id,
            provider="google",
            provider_user_id=sub,
            email=email,
            meta={"hd": idinfo.get("hd")}
        )
        db.add(identity)

    user.last_login_at = func.now()
    db.commit()
    db.refresh(user)
    return user
