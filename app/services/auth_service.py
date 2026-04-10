from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def signup(
        self,
        email: str,
        password: str,
        nickname: str,
    ) -> tuple[User, dict[str, str]]:
        existing_user = self.get_user_by_email(email=email)
        if existing_user is not None:
            raise AppException(code="CONFLICT", message="이미 가입된 이메일입니다.", status_code=409)

        user = User(
            email=email,
            nickname=nickname,
            hashed_password=hash_password(password=password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user, self._build_tokens(user_id=user.id)

    def login(
        self,
        email: str,
        password: str,
    ) -> tuple[User, dict[str, str]]:
        user = self.get_user_by_email(email=email)
        if user is None or not verify_password(password=password, hashed_password=user.hashed_password):
            raise AppException(code="UNAUTHORIZED", message="이메일 또는 비밀번호가 올바르지 않습니다.", status_code=401)

        return user, self._build_tokens(user_id=user.id)

    def refresh_access_token(self, refresh_token: str) -> dict[str, str]:
        payload = decode_token(token=refresh_token, expected_type="refresh")
        user_id = payload.get("sub")
        if not user_id:
            raise AppException(code="UNAUTHORIZED", message="유효하지 않은 토큰입니다.", status_code=401)

        user = self.get_user_by_id(user_id=user_id)
        if user is None:
            raise AppException(code="UNAUTHORIZED", message="사용자를 찾을 수 없습니다.", status_code=401)

        return {
            "access_token": create_access_token(subject=user.id),
            "token_type": "bearer",
        }

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: str) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def _build_tokens(self, user_id: str) -> dict[str, str]:
        return {
            "access_token": create_access_token(subject=user_id),
            "refresh_token": create_refresh_token(subject=user_id),
            "token_type": "bearer",
        }
