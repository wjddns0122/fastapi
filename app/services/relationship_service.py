from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.relationship import Relationship
from app.models.user import User


class RelationshipService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_relationship(
        self,
        current_user: User,
        target_user_id: str,
        relationship_type: str,
    ) -> Relationship:
        if current_user.id == target_user_id:
            raise AppException(
                code="BAD_REQUEST",
                message="자기 자신과의 관계는 생성할 수 없습니다.",
                status_code=400,
            )

        target_user = self.get_user_by_id(user_id=target_user_id)
        if target_user is None:
            raise AppException(
                code="NOT_FOUND",
                message="대상 사용자를 찾을 수 없습니다.",
                status_code=404,
            )

        existing_relationship = self._get_existing_relationship(
            first_user_id=current_user.id,
            second_user_id=target_user_id,
        )
        if existing_relationship is not None:
            raise AppException(
                code="CONFLICT",
                message="이미 관계 요청이 존재합니다.",
                status_code=409,
            )

        relationship = Relationship(
            requester_user_id=current_user.id,
            target_user_id=target_user_id,
            relationship_type=relationship_type,
            status="pending",
        )
        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)
        return relationship

    def accept_relationship(
        self,
        relationship_id: str,
        current_user: User,
    ) -> Relationship:
        relationship = self.get_relationship_by_id(relationship_id=relationship_id)
        if relationship is None:
            raise AppException(
                code="NOT_FOUND",
                message="관계 요청을 찾을 수 없습니다.",
                status_code=404,
            )

        if relationship.target_user_id != current_user.id:
            raise AppException(
                code="FORBIDDEN",
                message="관계 요청을 수락할 권한이 없습니다.",
                status_code=403,
            )

        if relationship.status != "pending":
            raise AppException(
                code="CONFLICT",
                message="이미 처리된 관계 요청입니다.",
                status_code=409,
            )

        relationship.status = "active"
        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)
        return relationship

    def list_my_relationships(self, current_user: User) -> list[dict[str, object]]:
        relationships = (
            self.db.query(Relationship)
            .filter(
                or_(
                    Relationship.requester_user_id == current_user.id,
                    Relationship.target_user_id == current_user.id,
                ),
            )
            .order_by(Relationship.id.desc())
            .all()
        )

        partner_ids = [
            relationship.target_user_id
            if relationship.requester_user_id == current_user.id
            else relationship.requester_user_id
            for relationship in relationships
        ]
        users = self.db.query(User).filter(User.id.in_(partner_ids)).all() if partner_ids else []
        user_map = {user.id: user for user in users}

        result: list[dict[str, object]] = []
        for relationship in relationships:
            partner_id = (
                relationship.target_user_id
                if relationship.requester_user_id == current_user.id
                else relationship.requester_user_id
            )
            partner = user_map.get(partner_id)
            if partner is None:
                continue

            result.append(
                {
                    "id": relationship.id,
                    "relationship_type": relationship.relationship_type,
                    "status": relationship.status,
                    "partner": {
                        "id": partner.id,
                        "nickname": partner.nickname,
                    },
                },
            )

        return result

    def get_relationship_by_id(self, relationship_id: str) -> Relationship | None:
        return self.db.query(Relationship).filter(Relationship.id == relationship_id).first()

    def get_user_by_id(self, user_id: str) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def _get_existing_relationship(
        self,
        first_user_id: str,
        second_user_id: str,
    ) -> Relationship | None:
        return (
            self.db.query(Relationship)
            .filter(
                or_(
                    and_(
                        Relationship.requester_user_id == first_user_id,
                        Relationship.target_user_id == second_user_id,
                    ),
                    and_(
                        Relationship.requester_user_id == second_user_id,
                        Relationship.target_user_id == first_user_id,
                    ),
                ),
            )
            .first()
        )
