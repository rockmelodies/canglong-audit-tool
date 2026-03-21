from __future__ import annotations

from dataclasses import dataclass
from secrets import token_urlsafe

from fastapi import Header, HTTPException, status

from app.models.schemas import UserProfile


@dataclass
class UserRecord:
    username: str
    password: str
    display_name: str
    role: str


class AuthService:
    def __init__(self) -> None:
        self._users = {
            "admin": UserRecord(
                username="admin",
                password="Canglong123!",
                display_name="Chief Auditor",
                role="administrator",
            )
        }
        self._tokens: dict[str, UserProfile] = {}

    def authenticate(self, username: str, password: str) -> UserProfile | None:
        user = self._users.get(username)
        if not user or user.password != password:
            return None

        return UserProfile(username=user.username, displayName=user.display_name, role=user.role)

    def create_token(self, user: UserProfile) -> str:
        token = token_urlsafe(24)
        self._tokens[token] = user
        return token

    def get_user_by_token(self, token: str) -> UserProfile | None:
        return self._tokens.get(token)


auth_service = AuthService()


def get_current_user(authorization: str | None = Header(default=None)) -> UserProfile:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    token = authorization.removeprefix("Bearer ").strip()
    user = auth_service.get_user_by_token(token)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return user

