from fastapi import HTTPException, status

from app.core.config import Settings
from app.core.security import create_access_token


class AuthService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def issue_token(self, username: str, password: str) -> dict:
        if username != self.settings.auth_username or password != self.settings.auth_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.",
            )
        token = create_access_token(subject=username, settings=self.settings)
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in_seconds": self.settings.access_token_expire_minutes * 60,
        }

