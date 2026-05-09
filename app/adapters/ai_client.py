from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.core.exceptions import AppException


@dataclass(frozen=True)
class TarotInterpretationPrompt:
    question: str
    relationship_type: str
    card_name: str
    card_orientation: str


class GeminiAIClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        self._http_client = httpx.Client(timeout=settings.gemini_request_timeout_seconds)

    def close(self) -> None:
        self._http_client.close()

    def generate_tarot_interpretation(
        self,
        prompt: TarotInterpretationPrompt,
    ) -> str:
        if not self.api_key:
            raise AppException(
                code="INTERNAL_SERVER_ERROR",
                message="Gemini API 설정이 누락되었습니다.",
                status_code=500,
            )

        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/{self.model}:generateContent"
        )
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": self._build_prompt_text(prompt=prompt)}],
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 160,
            },
        }

        response = self._http_client.post(endpoint, headers=headers, json=payload)
        if response.status_code >= 400:
            raise AppException(
                code="INTERNAL_SERVER_ERROR",
                message="Gemini API 요청에 실패했습니다.",
                status_code=500,
            )

        return self._extract_text(response=response)

    @staticmethod
    def _build_prompt_text(prompt: TarotInterpretationPrompt) -> str:
        return (
            "연애/관계 맥락의 오늘의 타로 해석을 한국어로 작성해주세요.\n"
            "규칙: 1~2문장, 부드럽고 간결한 톤, 단정적 예언과 공포 조장 금지, "
            "가능하면 가벼운 행동 제안 1개 포함.\n"
            f"관계 유형: {prompt.relationship_type}\n"
            f"질문: {prompt.question}\n"
            f"카드: {prompt.card_name}\n"
            f"방향: {prompt.card_orientation}\n"
        )

    @staticmethod
    def _extract_text(response: httpx.Response) -> str:
        try:
            response_body = response.json()
        except ValueError as exc:
            raise AppException(
                code="INTERNAL_SERVER_ERROR",
                message="Gemini API 응답이 올바르지 않습니다.",
                status_code=500,
            ) from exc

        candidates = response_body.get("candidates") or []
        if not candidates:
            raise AppException(
                code="INTERNAL_SERVER_ERROR",
                message="Gemini API 응답이 비어 있습니다.",
                status_code=500,
            )

        parts = candidates[0].get("content", {}).get("parts", [])
        texts = [
            part.get("text", "").strip()
            for part in parts
            if part.get("text")
        ]
        interpretation = " ".join(texts).strip()
        if not interpretation:
            raise AppException(
                code="INTERNAL_SERVER_ERROR",
                message="Gemini API 해석 결과가 비어 있습니다.",
                status_code=500,
            )

        return interpretation[:500]
