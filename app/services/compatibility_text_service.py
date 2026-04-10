from __future__ import annotations

from app.services.compatibility_engine import TarotResult


class CompatibilityTextService:
    def build_summary(
        self,
        final_score: int,
        tarot_result: TarotResult,
        behavior_score: int,
    ) -> str:
        if final_score >= 85:
            return "오늘은 호흡이 잘 맞는 날입니다. 가벼운 대화도 따뜻하게 이어질 가능성이 높아요."
        if final_score >= 70:
            if behavior_score >= 8:
                return "전반적으로 좋은 흐름입니다. 함께 쌓인 활동 덕분에 분위기가 더 부드럽게 이어질 수 있어요."
            return "전반적으로 좋은 흐름입니다. 작은 표현이 분위기를 더 부드럽게 만들 수 있어요."
        if final_score >= 55:
            return "무난한 흐름이지만, 표현이 부족하면 거리감이 생길 수 있습니다."
        if final_score >= 40:
            if tarot_result.score < 0:
                return "오늘은 서로의 말이 조금 다르게 들릴 수 있습니다. 해석보다 확인이 더 중요한 날이에요."
            return "오늘은 서로의 말이 조금 다르게 들릴 수 있습니다."
        return "예민함이 쌓일 수 있는 날입니다. 작은 오해가 커지지 않도록 주의가 필요합니다."

    def build_prescription(
        self,
        final_score: int,
        tarot_result: TarotResult,
        behavior_score: int,
        behavior_metrics: dict[str, int | bool],
    ) -> str:
        if behavior_score <= 0:
            if int(behavior_metrics.get("shop_visits_last_1d", 0)) == 0:
                return "오늘은 먼저 안부를 건네고, 시간이 된다면 상점에 들러 작은 변화를 줘보세요."
            return "먼저 안부를 건네며 대화를 시작해보세요."

        if tarot_result.score < 0:
            return "오늘은 해석보다 공감이 먼저입니다. 짧고 부드러운 표현으로 분위기를 풀어보세요."

        if bool(behavior_metrics.get("pair_matching_outfit", False)):
            return "좋은 흐름이 이어지고 있습니다. 커플 코디를 맞춘 김에 가벼운 칭찬도 함께 건네보세요."

        if int(behavior_metrics.get("avatar_changes_last_1d", 0)) == 0:
            return "가벼운 칭찬 한 마디를 먼저 건네고, 아바타 스타일도 한 번 바꿔보세요."

        if final_score >= 70:
            return "가벼운 리액션이나 다정한 답장을 먼저 남겨보세요."

        if final_score >= 55:
            return "오늘은 먼저 안부를 묻거나 짧은 편지를 남겨보세요."

        if final_score >= 40:
            return "답을 서두르기보다 상대의 기분을 먼저 확인해보세요."

        return "중요한 이야기는 미루고, 부드러운 한마디만 남겨보세요."
