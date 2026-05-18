"""
JWT AUTH
Versioning
Query String, Pagination
Idempotency
Rate Limiting

Celery - Django (Async)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.routes import auth_manual, auth_google, goals, auth_refresh, verifications, user, payments
from src.gpt import apicalls# no leading dot
from src.config import settings
from src.helpers.limiter import limiter
import logging
logging.basicConfig(level=logging.INFO)



app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS for mobile app development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_manual.router)
app.include_router(auth_google.router)
app.include_router(goals.router)
app.include_router(auth_refresh.router)
app.include_router(verifications.router)
app.include_router(user.router)
app.include_router(payments.router)