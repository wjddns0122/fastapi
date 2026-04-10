from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date

from app.models.relationship import Relationship


@dataclass(frozen=True)
class TarotResult:
    card_name: str
    orientation: str
    score: int


class CompatibilityEngine:
    _RELATIONSHIP_TYPE_BASE_SCORES: dict[str, int] = {
        "couple": 64,
        "situationship": 58,
        "friend": 61,
    }

    _TAROT_SCORE_TABLE: dict[str, dict[str, int]] = {
        "The Sun": {"upright": 12, "reversed": 4},
        "The Lovers": {"upright": 10, "reversed": 3},
        "Temperance": {"upright": 8, "reversed": 2},
        "The Star": {"upright": 7, "reversed": 3},
        "Wheel of Fortune": {"upright": 5, "reversed": 1},
        "The Moon": {"upright": -4, "reversed": -2},
        "The Devil": {"upright": -7, "reversed": -4},
        "The Tower": {"upright": -10, "reversed": -6},
    }

    def build_initial_base_score(
        self,
        requester_user_id: str,
        target_user_id: str,
        relationship_type: str,
    ) -> int:
        seed = self._seed_int(
            ":".join(sorted([requester_user_id, target_user_id])) + f":{relationship_type}",
        )
        modifier = (seed % 11) - 4
        base_score = self._RELATIONSHIP_TYPE_BASE_SCORES[relationship_type] + modifier
        return self._clamp(base_score, 50, 75)

    def get_tarot_result(
        self,
        relationship_id: str,
        target_date: date,
    ) -> TarotResult:
        seed = self._seed_int(f"{relationship_id}:{target_date.isoformat()}:tarot")
        card_names = list(self._TAROT_SCORE_TABLE.keys())
        card_name = card_names[seed % len(card_names)]
        orientation = "upright" if ((seed // len(card_names)) % 2 == 0) else "reversed"
        score = self._TAROT_SCORE_TABLE[card_name][orientation]
        return TarotResult(card_name=card_name, orientation=orientation, score=score)

    def score_behavior(self, behavior_metrics: dict[str, int | bool]) -> int:
        score = 0

        if int(behavior_metrics.get("letters_sent_last_1d", 0)) > 0:
            score += 4
        if int(behavior_metrics.get("letters_opened_last_1d", 0)) > 0:
            score += 2

        daily_quests_completed = int(behavior_metrics.get("daily_quests_completed_last_1d", 0))
        if daily_quests_completed >= 3:
            score += 5
        elif daily_quests_completed > 0:
            score += 3

        if int(behavior_metrics.get("weekly_quests_completed_last_7d", 0)) > 0:
            score += 6
        if int(behavior_metrics.get("shop_visits_last_1d", 0)) > 0:
            score += 1
        if int(behavior_metrics.get("avatar_changes_last_1d", 0)) > 0:
            score += 2
        if int(behavior_metrics.get("couple_items_equipped_last_1d", 0)) > 0:
            score += 2
        if bool(behavior_metrics.get("pair_matching_outfit", False)):
            score += 5

        checkins_completed = int(behavior_metrics.get("checkins_completed_last_1d", 0))
        if checkins_completed > 0:
            score += 2
        if bool(behavior_metrics.get("pair_checkins_completed_last_1d", False)):
            score += 4

        streak_days = int(behavior_metrics.get("streak_days", 0))
        if streak_days >= 7:
            score += 5
        elif streak_days >= 3:
            score += 3

        inactive_days = int(behavior_metrics.get("inactive_days", 0))
        if inactive_days >= 3:
            score -= 8

        if score == 0:
            score -= 4

        return self._clamp(score, -10, 15)

    def get_adjustment(
        self,
        relationship_id: str,
        target_date: date,
        pre_adjust_score: int,
    ) -> int:
        if pre_adjust_score > 92:
            return -3
        if pre_adjust_score < 35:
            return 4

        seed = self._seed_int(f"{relationship_id}:{target_date.isoformat()}:adjustment")
        return (seed % 3) - 1

    def get_final_score(
        self,
        base_score: int,
        tarot_score: int,
        behavior_score: int,
        adjustment: int,
    ) -> int:
        return self._clamp(base_score + tarot_score + behavior_score + adjustment, 0, 100)

    @staticmethod
    def _seed_int(seed_text: str) -> int:
        digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
        return int(digest, 16)

    @staticmethod
    def _clamp(value: int, minimum: int, maximum: int) -> int:
        return max(minimum, min(maximum, value))
