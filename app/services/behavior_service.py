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
        seven_day_start = target_date - timedelta(days=6)

        today_activities = (
            self.db.query(RelationshipActivity)
            .filter(
                RelationshipActivity.relationship_id == relationship.id,
                RelationshipActivity.occurred_on == target_date,
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
        inactive_days = (
            0
            if latest_activity_date is None
            else max(0, (target_date - latest_activity_date).days)
        )

        participants = {
            relationship.requester_user_id,
            relationship.target_user_id,
        }
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
            "letters_sent_last_1d": self._count_events(today_activities, "letter_sent"),
            "letters_opened_last_1d": self._count_events(today_activities, "letter_opened"),
            "daily_quests_completed_last_1d": self._count_events(today_activities, "daily_quest_completed"),
            "weekly_quests_completed_last_7d": self._count_events(weekly_activities, "weekly_quest_completed"),
            "shop_visits_last_1d": self._count_events(today_activities, "shop_visited"),
            "avatar_changes_last_1d": self._count_events(today_activities, "avatar_changed"),
            "couple_items_equipped_last_1d": self._count_events(today_activities, "couple_item_equipped"),
            "pair_matching_outfit": couple_item_user_ids == participants,
            "checkins_completed_last_1d": self._count_events(today_activities, "checkin_completed"),
            "pair_checkins_completed_last_1d": checkin_user_ids == participants,
            "streak_days": streak_days,
            "inactive_days": inactive_days,
        }

    def _calculate_streak_days(
        self,
        relationship_id: str,
        target_date: date,
        max_lookback_days: int = 365,
    ) -> int:
        oldest = target_date - timedelta(days=max_lookback_days - 1)  # inclusive range
        active_dates = {
            row[0]
            for row in self.db.query(RelationshipActivity.occurred_on)
            .filter(
                RelationshipActivity.relationship_id == relationship_id,
                RelationshipActivity.occurred_on >= oldest,
                RelationshipActivity.occurred_on <= target_date,
            )
            .distinct()
            .all()
        }
        streak_days = 0
        current_date = target_date
        while current_date in active_dates:
            streak_days += 1
            current_date -= timedelta(days=1)
        return streak_days

    @staticmethod
    def _count_events(
        activities: list[RelationshipActivity],
        event_type: str,
    ) -> int:
        return sum(1 for activity in activities if activity.event_type == event_type)
