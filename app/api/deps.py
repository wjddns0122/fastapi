from collections.abc import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.adapters.ai_client import GeminiAIClient
from app.adapters.storage_client import SupabaseStorageClient
from app.core.db import SessionLocal
from app.core.exceptions import AppException
from app.core.security import decode_token
from app.models.user import User
from app.services.activity_service import ActivityService
from app.services.auth_service import AuthService
from app.services.behavior_service import BehaviorService
from app.services.compatibility_engine import CompatibilityEngine
from app.services.compatibility_service import CompatibilityService
from app.services.compatibility_text_service import CompatibilityTextService
from app.services.letter_service import LetterService
from app.services.mission_service import MissionService
from app.services.relationship_service import RelationshipService
from app.services.report_service import ReportService
from app.services.tarot_service import TarotService
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


def get_relationship_service(db: Session = Depends(get_db)) -> RelationshipService:
    return RelationshipService(db=db)


def get_compatibility_service(
    db: Session = Depends(get_db),
) -> CompatibilityService:
    return CompatibilityService(
        db=db,
        behavior_service=BehaviorService(db=db),
        compatibility_engine=CompatibilityEngine(),
        compatibility_text_service=CompatibilityTextService(),
    )


def get_activity_service(db: Session = Depends(get_db)) -> ActivityService:
    return ActivityService(db=db)


def get_letter_service(db: Session = Depends(get_db)) -> LetterService:
    return LetterService(db=db)


def get_mission_service(db: Session = Depends(get_db)) -> MissionService:
    return MissionService(db=db)


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    return ReportService(db=db)


def get_tarot_ai_client() -> Generator[GeminiAIClient, None, None]:
    client = GeminiAIClient()
    try:
        yield client
    finally:
        client.close()


def get_tarot_service(
    db: Session = Depends(get_db),
    ai_client: GeminiAIClient = Depends(get_tarot_ai_client),
) -> TarotService:
    return TarotService(db=db, ai_client=ai_client)


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
