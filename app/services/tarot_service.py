from __future__ import annotations

import hashlib
import logging
from datetime import date

import httpx
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.adapters.ai_client import GeminiAIClient, TarotInterpretationPrompt
from app.core.exceptions import AppException
from app.models.daily_tarot import DailyTarot
from app.models.relationship import Relationship
from app.models.user import User

logger = logging.getLogger(__name__)


class TarotService:
    _MAJOR_ARCANA: tuple[str, ...] = (
        "The Fool",
        "The Magician",
        "The High Priestess",
        "The Empress",
        "The Emperor",
        "The Hierophant",
        "The Lovers",
        "The Chariot",
        "Strength",
        "The Hermit",
        "Wheel of Fortune",
        "Justice",
        "The Hanged Man",
        "Death",
        "Temperance",
        "The Devil",
        "The Tower",
        "The Star",
        "The Moon",
        "The Sun",
        "Judgement",
        "The World",
    )

    _FALLBACK_INTERPRETATIONS: dict[str, str] = {
        "The Fool": "새로운 시도를 가볍게 시작하기 좋은 날입니다. 부담을 주기보다 자연스럽게 말을 건네보세요.",
        "The Magician": "표현력이 살아나는 흐름입니다. 짧지만 분명한 말이 관계의 분위기를 바꿀 수 있습니다.",
        "The High Priestess": "오늘은 감정보다 직관이 먼저 움직일 수 있습니다. 서두르지 말고 상대의 반응을 차분히 살펴보세요.",
        "The Empress": "따뜻한 표현이 잘 전달되는 날입니다. 다정한 한마디가 관계를 부드럽게 만들 수 있습니다.",
        "The Emperor": "분명한 태도가 필요한 날입니다. 다만 단호함보다 안정감을 주는 표현이 더 적합합니다.",
        "The Hierophant": "익숙하고 편안한 방식이 잘 맞는 날입니다. 평소처럼 안부를 묻는 것부터 시작해보세요.",
        "The Lovers": "서로의 마음을 확인하기 좋은 흐름입니다. 가벼운 관심 표현이 자연스럽게 이어질 수 있습니다.",
        "The Chariot": "관계를 앞으로 움직일 힘이 있는 날입니다. 망설이기보다 짧은 연락으로 흐름을 만들어보세요.",
        "Strength": "부드러운 인내가 더 좋은 반응을 이끌 수 있습니다. 강하게 밀어붙이기보다 따뜻하게 다가가세요.",
        "The Hermit": "혼자 생각할 시간이 필요한 흐름입니다. 긴 대화보다 짧은 배려 표현이 더 편안할 수 있습니다.",
        "Wheel of Fortune": "분위기가 예상보다 빠르게 바뀔 수 있습니다. 작은 계기를 만들어보면 흐름이 좋아질 수 있습니다.",
        "Justice": "오늘은 균형 잡힌 말이 중요합니다. 감정보다 사실과 배려를 함께 담아 표현해보세요.",
        "The Hanged Man": "바로 답을 얻으려 하기보다 한 박자 기다리는 편이 좋습니다. 천천히 접근해보세요.",
        "Death": "관계의 낡은 흐름을 바꿀 기회가 있습니다. 무거운 말보다 새로운 방식의 표현을 시도해보세요.",
        "Temperance": "오늘은 서두르기보다 균형 있게 접근하는 편이 좋습니다. 짧고 부드러운 연락이 자연스럽습니다.",
        "The Devil": "집착이나 불안이 커질 수 있는 날입니다. 확인을 요구하기보다 편안한 안부로 시작해보세요.",
        "The Tower": "감정이 예민해질 수 있는 날입니다. 중요한 말은 서두르지 않는 편이 좋습니다.",
        "The Star": "회복과 기대감이 살아나는 흐름입니다. 작은 응원이 관계에 긍정적으로 닿을 수 있습니다.",
        "The Moon": "오해나 추측이 생기기 쉬운 날입니다. 넘겨짚기보다 부드럽게 확인해보세요.",
        "The Sun": "밝은 흐름이 강한 날입니다. 가벼운 표현도 좋은 반응으로 이어질 가능성이 큽니다.",
        "Judgement": "미뤄둔 마음을 정리하기 좋은 날입니다. 솔직하지만 부담 없는 표현을 선택해보세요.",
        "The World": "관계의 흐름이 안정적으로 마무리되는 날입니다. 감사나 칭찬을 전하기 좋습니다.",
    }

    def __init__(
        self,
        db: Session,
        ai_client: GeminiAIClient,
    ) -> None:
        self.db = db
        self.ai_client = ai_client

    def create_daily_tarot(
        self,
        current_user: User,
        relationship_id: str,
        question: str,
        target_date: date,
    ) -> tuple[DailyTarot, bool]:
        relationship = self._get_accessible_relationship(
            current_user=current_user,
            relationship_id=relationship_id,
        )
        existing_tarot = self.get_daily_tarot(
            user_id=current_user.id,
            relationship_id=relationship.id,
            target_date=target_date,
        )
        if existing_tarot is not None:
            return existing_tarot, False

        card_name, card_orientation = self._draw_card(
            user_id=current_user.id,
            relationship_id=relationship.id,
            target_date=target_date,
        )
        ai_interpretation = self._generate_interpretation(
            relationship=relationship,
            question=question,
            card_name=card_name,
            card_orientation=card_orientation,
        )

        daily_tarot = DailyTarot(
            user_id=current_user.id,
            relationship_id=relationship.id,
            target_date=target_date,
            question=question,
            card_name=card_name,
            card_orientation=card_orientation,
            ai_interpretation=ai_interpretation,
        )
        self.db.add(daily_tarot)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            existing_after_race = self.get_daily_tarot(
                user_id=current_user.id,
                relationship_id=relationship.id,
                target_date=target_date,
            )
            if existing_after_race is None:
                raise
            return existing_after_race, False
        self.db.refresh(daily_tarot)
        return daily_tarot, True

    def list_daily_tarot_history(
        self,
        current_user: User,
        relationship_id: str | None = None,
    ) -> list[DailyTarot]:
        query = self.db.query(DailyTarot).filter(DailyTarot.user_id == current_user.id)
        if relationship_id is not None:
            self._get_accessible_relationship(
                current_user=current_user,
                relationship_id=relationship_id,
            )
            query = query.filter(DailyTarot.relationship_id == relationship_id)

        return query.order_by(DailyTarot.target_date.desc(), DailyTarot.created_at.desc()).all()

    def get_daily_tarot(
        self,
        user_id: str,
        relationship_id: str,
        target_date: date,
    ) -> DailyTarot | None:
        return (
            self.db.query(DailyTarot)
            .filter(
                DailyTarot.user_id == user_id,
                DailyTarot.relationship_id == relationship_id,
                DailyTarot.target_date == target_date,
            )
            .first()
        )

    def _get_accessible_relationship(
        self,
        current_user: User,
        relationship_id: str,
    ) -> Relationship:
        relationship = (
            self.db.query(Relationship)
            .filter(Relationship.id == relationship_id)
            .first()
        )
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
                message="타로를 조회할 권한이 없습니다.",
                status_code=403,
            )

        if relationship.status != "accepted":
            raise AppException(
                code="CONFLICT",
                message="수락된 관계만 타로를 뽑을 수 있습니다.",
                status_code=409,
            )

        return relationship

    def _generate_interpretation(
        self,
        relationship: Relationship,
        question: str,
        card_name: str,
        card_orientation: str,
    ) -> str:
        try:
            return self.ai_client.generate_tarot_interpretation(
                prompt=TarotInterpretationPrompt(
                    question=question,
                    relationship_type=relationship.relationship_type,
                    card_name=card_name,
                    card_orientation=card_orientation,
                ),
            )
        except (AppException, httpx.HTTPError) as exc:
            logger.warning(
                "Gemini interpretation failed, using fallback (card=%s, orientation=%s): %s",
                card_name,
                card_orientation,
                exc,
            )
            return self._build_fallback_interpretation(
                card_name=card_name,
                card_orientation=card_orientation,
            )

    def _build_fallback_interpretation(
        self,
        card_name: str,
        card_orientation: str,
    ) -> str:
        interpretation = self._FALLBACK_INTERPRETATIONS[card_name]
        if card_orientation == "reversed":
            return f"{interpretation} 다만 오늘은 반응을 재촉하지 않는 태도가 더 중요합니다."
        return interpretation

    def _draw_card(
        self,
        user_id: str,
        relationship_id: str,
        target_date: date,
    ) -> tuple[str, str]:
        seed = self._seed_int(f"{user_id}:{relationship_id}:{target_date.isoformat()}")
        card_name = self._MAJOR_ARCANA[seed % len(self._MAJOR_ARCANA)]
        orientation = "upright" if ((seed // len(self._MAJOR_ARCANA)) % 2 == 0) else "reversed"
        return card_name, orientation

    @staticmethod
    def _seed_int(seed_text: str) -> int:
        digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
        return int(digest, 16)
