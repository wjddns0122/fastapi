from datetime import date

import httpx

from app.core.exceptions import AppException
from app.models.daily_tarot import DailyTarot
from app.services.auth_service import AuthService
from app.services.relationship_service import RelationshipService
from app.services.tarot_service import TarotService


class FailingTarotAIClient:
    def generate_tarot_interpretation(self, prompt):
        raise httpx.ConnectError("AI 요청 실패")


class FakeTarotAIClient:
    def generate_tarot_interpretation(self, prompt):
        return "Gemini 해석 결과입니다."


def _create_accepted_relationship(db_session):
    auth_service = AuthService(db=db_session)
    requester, _ = auth_service.signup(
        email="requester@example.com",
        password="StrongPassword123!",
        nickname="requester",
    )
    target, _ = auth_service.signup(
        email="target@example.com",
        password="StrongPassword123!",
        nickname="target",
    )
    relationship_service = RelationshipService(db=db_session)
    relationship = relationship_service.create_relationship(
        current_user=requester,
        target_user_id=target.id,
        relationship_type="couple",
    )
    relationship_service.accept_relationship(
        relationship_id=relationship.id,
        current_user=target,
    )

    return requester, relationship


def _create_pending_relationship(db_session):
    auth_service = AuthService(db=db_session)
    requester, _ = auth_service.signup(
        email="pending-requester@example.com",
        password="StrongPassword123!",
        nickname="requester",
    )
    target, _ = auth_service.signup(
        email="pending-target@example.com",
        password="StrongPassword123!",
        nickname="target",
    )
    relationship_service = RelationshipService(db=db_session)
    relationship = relationship_service.create_relationship(
        current_user=requester,
        target_user_id=target.id,
        relationship_type="couple",
    )

    return requester, relationship


def test_tarot_service_creates_daily_tarot_with_ai_interpretation(db_session):
    requester, relationship = _create_accepted_relationship(db_session)
    service = TarotService(db=db_session, ai_client=FakeTarotAIClient())

    daily_tarot, created = service.create_daily_tarot(
        current_user=requester,
        relationship_id=relationship.id,
        question="오늘 연락해도 될까?",
        target_date=date(2026, 4, 10),
    )

    assert created is True
    assert daily_tarot.id
    assert daily_tarot.ai_interpretation == "Gemini 해석 결과입니다."
    assert daily_tarot.card_name
    assert daily_tarot.card_orientation in {"upright", "reversed"}


def test_tarot_service_returns_existing_daily_tarot(db_session):
    requester, relationship = _create_accepted_relationship(db_session)
    service = TarotService(db=db_session, ai_client=FakeTarotAIClient())

    first, first_created = service.create_daily_tarot(
        current_user=requester,
        relationship_id=relationship.id,
        question="첫 질문",
        target_date=date(2026, 4, 10),
    )
    second, second_created = service.create_daily_tarot(
        current_user=requester,
        relationship_id=relationship.id,
        question="다른 질문",
        target_date=date(2026, 4, 10),
    )

    assert first_created is True
    assert second_created is False
    assert first.id == second.id
    assert second.question == "첫 질문"


def test_tarot_service_uses_fallback_when_ai_fails(db_session):
    requester, relationship = _create_accepted_relationship(db_session)
    service = TarotService(db=db_session, ai_client=FailingTarotAIClient())

    daily_tarot, created = service.create_daily_tarot(
        current_user=requester,
        relationship_id=relationship.id,
        question="오늘 연락해도 될까?",
        target_date=date(2026, 4, 10),
    )

    assert created is True
    assert daily_tarot.ai_interpretation
    assert daily_tarot.ai_interpretation != "Gemini 해석 결과입니다."


def test_tarot_service_propagates_unknown_ai_errors(db_session):
    class CrashingTarotAIClient:
        def generate_tarot_interpretation(self, prompt):
            raise RuntimeError("예상치 못한 오류")

    requester, relationship = _create_accepted_relationship(db_session)
    service = TarotService(db=db_session, ai_client=CrashingTarotAIClient())

    try:
        service.create_daily_tarot(
            current_user=requester,
            relationship_id=relationship.id,
            question="오늘 연락해도 될까?",
            target_date=date(2026, 4, 10),
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("RuntimeError가 전파되어야 합니다.")


def test_tarot_service_uses_tarot_specific_conflict_message(db_session):
    requester, relationship = _create_pending_relationship(db_session)
    service = TarotService(db=db_session, ai_client=FakeTarotAIClient())

    try:
        service.create_daily_tarot(
            current_user=requester,
            relationship_id=relationship.id,
            question="오늘 연락해도 될까?",
            target_date=date(2026, 4, 10),
        )
    except AppException as exc:
        assert exc.code == "CONFLICT"
        assert exc.message == "수락된 관계만 타로를 뽑을 수 있습니다."
    else:
        raise AssertionError("AppException이 발생해야 합니다.")


def test_tarot_service_returns_existing_when_concurrent_insert_races(db_session):
    requester, relationship = _create_accepted_relationship(db_session)
    service = TarotService(db=db_session, ai_client=FakeTarotAIClient())
    target_date = date(2026, 4, 10)

    pre_existing = DailyTarot(
        user_id=requester.id,
        relationship_id=relationship.id,
        target_date=target_date,
        question="먼저 들어온 질문",
        card_name="The Sun",
        card_orientation="upright",
        ai_interpretation="먼저 저장된 해석",
    )
    db_session.add(pre_existing)
    db_session.commit()

    original_get_daily_tarot = service.get_daily_tarot
    call_count = {"value": 0}

    def get_daily_tarot_after_first_call(**kwargs):
        call_count["value"] += 1
        if call_count["value"] == 1:
            return None
        return original_get_daily_tarot(**kwargs)

    service.get_daily_tarot = get_daily_tarot_after_first_call

    result, created = service.create_daily_tarot(
        current_user=requester,
        relationship_id=relationship.id,
        question="다른 질문",
        target_date=target_date,
    )

    assert created is False
    assert result.id == pre_existing.id
    assert result.question == "먼저 들어온 질문"


def test_relationship_delete_cascades_daily_tarot_records(db_session):
    requester, relationship = _create_accepted_relationship(db_session)
    service = TarotService(db=db_session, ai_client=FakeTarotAIClient())
    service.create_daily_tarot(
        current_user=requester,
        relationship_id=relationship.id,
        question="오늘 연락해도 될까?",
        target_date=date(2026, 4, 10),
    )
    assert (
        db_session.query(DailyTarot)
        .filter(DailyTarot.relationship_id == relationship.id)
        .count()
        == 1
    )

    relationship_service = RelationshipService(db=db_session)
    relationship_service.delete_relationship(
        relationship_id=relationship.id,
        current_user=requester,
    )

    assert (
        db_session.query(DailyTarot)
        .filter(DailyTarot.relationship_id == relationship.id)
        .count()
        == 0
    )
