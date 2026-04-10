from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.relationship import Relationship
from app.models.relationship_activity import RelationshipActivity


class BehaviorService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def aggregate_recent_behavior(
        self,
        relationship: Relationship,
        target_date: date,
    ) -> dict[str, int | bool]:
        one_day_start = target_date - timedelta(days=1)
        seven_day_start = target_date - timedelta(days=6)

        recent_activities = (
            self.db.query(RelationshipActivity)
            .filter(
                RelationshipActivity.relationship_id == relationship.id,
                RelationshipActivity.occurred_on >= one_day_start,
                RelationshipActivity.occurred_on <= target_date,
            )
            .all()
        )
        weekly_activities = (
            self.db.query(RelationshipActivity)
            .filter(
                RelationshipActivity.relationship_id == relationship.id,
                RelationshipActivity.occurred_on >= seven_day_start,
                RelationshipActivity.occurred_on <= target_date,
            )
            .all()
        )

        latest_activity_date = (
            self.db.query(func.max(RelationshipActivity.occurred_on))
            .filter(RelationshipActivity.relationship_id == relationship.id)
            .scalar()
        )
        inactive_days = 0 if latest_activity_date is None else (target_date - latest_activity_date).days

        participants = {
            relationship.requester_user_id,
            relationship.target_user_id,
        }
        today_activities = [
            activity
            for activity in recent_activities
            if activity.occurred_on == target_date
        ]
        checkin_user_ids = {
            activity.actor_user_id
            for activity in today_activities
            if activity.event_type == "checkin_completed"
        }
        couple_item_user_ids = {
            activity.actor_user_id
            for activity in today_activities
            if activity.event_type == "couple_item_equipped"
        }

        streak_days = self._calculate_streak_days(
            relationship_id=relationship.id,
            target_date=target_date,
        )

        return {
            "letters_sent_last_1d": self._count_events(recent_activities, "letter_sent"),
            "letters_opened_last_1d": self._count_events(recent_activities, "letter_opened"),
            "daily_quests_completed_last_1d": self._count_events(recent_activities, "daily_quest_completed"),
            "weekly_quests_completed_last_7d": self._count_events(weekly_activities, "weekly_quest_completed"),
            "shop_visits_last_1d": self._count_events(recent_activities, "shop_visited"),
            "avatar_changes_last_1d": self._count_events(recent_activities, "avatar_changed"),
            "couple_items_equipped_last_1d": self._count_events(recent_activities, "couple_item_equipped"),
            "pair_matching_outfit": couple_item_user_ids == participants,
            "checkins_completed_last_1d": self._count_events(recent_activities, "checkin_completed"),
            "pair_checkins_completed_last_1d": checkin_user_ids == participants,
            "streak_days": streak_days,
            "inactive_days": inactive_days,
        }

    def _calculate_streak_days(
        self,
        relationship_id: str,
        target_date: date,
    ) -> int:
        streak_days = 0
        current_date = target_date

        while True:
            has_activity = (
                self.db.query(RelationshipActivity.id)
                .filter(
                    RelationshipActivity.relationship_id == relationship_id,
                    RelationshipActivity.occurred_on == current_date,
                )
                .first()
                is not None
            )
            if not has_activity:
                break

            streak_days += 1
            current_date -= timedelta(days=1)

        return streak_days

    @staticmethod
    def _count_events(
        activities: list[RelationshipActivity],
        event_type: str,
    ) -> int:
        return sum(1 for activity in activities if activity.event_type == event_type)
