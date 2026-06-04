import datetime as dt
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class Principal:
    user_id: str
    auth_type: str


def create_access_token(subject: str, settings: Settings) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    exp = now + dt.timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        ) from exc


async def get_current_principal(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> Principal:
    api_key = request.headers.get("x-api-key", "").strip()

    if settings.auth_required:
        if settings.static_api_key and api_key == settings.static_api_key:
            principal = Principal(user_id="api-key-client", auth_type="api_key")
            request.state.user_id = principal.user_id
            return principal

        if credentials and credentials.scheme.lower() == "bearer":
            payload = decode_access_token(credentials.credentials, settings)
            user_id = str(payload.get("sub", "")).strip()
            if user_id:
                principal = Principal(user_id=user_id, auth_type="jwt")
                request.state.user_id = principal.user_id
                return principal

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    # Development mode fallback
    principal = Principal(user_id="anonymous", auth_type="none")
    request.state.user_id = principal.user_id
    return principal

