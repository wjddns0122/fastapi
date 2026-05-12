from app.core.exceptions import AppException
from app.models.relationship import Relationship
from app.models.user import User


def ensure_relationship_access(
    relationship: Relationship | None,
    current_user: User,
    forbidden_message: str,
    conflict_message: str = "수락된 관계에서만 사용할 수 있습니다.",
) -> Relationship:
    """관계 존재 여부와 현재 사용자의 접근 권한을 검증합니다."""
    if relationship is None:
        raise AppException(
            code="NOT_FOUND",
            message="관계를 찾을 수 없습니다.",
            status_code=404,
        )

    is_participant = current_user.id in {
        relationship.requester_user_id,
        relationship.target_user_id,
    }
    if not is_participant:
        raise AppException(
            code="FORBIDDEN",
            message=forbidden_message,
            status_code=403,
        )

    if relationship.status != "accepted":
        raise AppException(
            code="CONFLICT",
            message=conflict_message,
            status_code=409,
        )

    return relationship
