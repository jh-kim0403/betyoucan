from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from jose import jwt, JWTError
from ..config import settings


def _get_user_id_key(request: Request) -> str:
    """
    Rate-limit key: user_id extracted from the JWT when present,
    falls back to the remote IP for unauthenticated requests.
    """
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except JWTError:
            pass
    return get_remote_address(request)


limiter = Limiter(
    key_func=_get_user_id_key,
    storage_uri=settings.slowapi_redis_url,
)
