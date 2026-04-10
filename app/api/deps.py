from collections.abc import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.adapters.storage_client import SupabaseStorageClient
from app.core.db import SessionLocal
from app.core.exceptions import AppException
from app.core.security import decode_token
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.user_service import UserService

bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db=db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db=db)


def get_storage_client() -> Generator[SupabaseStorageClient, None, None]:
    client = SupabaseStorageClient()
    try:
        yield client
    finally:
        client.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    if credentials is None:
        raise AppException(code="UNAUTHORIZED", message="인증이 필요합니다.", status_code=401)

    payload = decode_token(token=credentials.credentials, expected_type="access")
    user_id = payload.get("sub")
    if not user_id:
        raise AppException(code="UNAUTHORIZED", message="유효하지 않은 토큰입니다.", status_code=401)

    user = auth_service.get_user_by_id(user_id=user_id)
    if user is None:
        raise AppException(code="UNAUTHORIZED", message="사용자를 찾을 수 없습니다.", status_code=401)

    return user
