from app.schemas.base import CamelModel
from typing import Any, Generic, TypeVar
from pydantic import Field

T = TypeVar("T")

class SuccessResponseSchema(CamelModel, Generic[T]):
    """성공 응답 스키마"""
    success: bool = Field(default=True, description="성공 여부 (항상 true)", examples=[True])
    data: T = Field(description="요청에 따른 실제 응답 데이터")
    message: str = Field(default="OK", description="응답 메시지", examples=["OK"])


class ErrorDetailSchema(CamelModel):
    """에러 상세 정보"""
    code: str = Field(description="에러 코드 (예: UNAUTHORIZED, NOT_FOUND)", examples=["UNAUTHORIZED"])
    message: str = Field(description="사람이 읽을 수 있는 에러 설명", examples=["인증이 필요합니다."])
    details: Any | None = Field(default=None, description="추가 디버그 정보 (VALIDATION_ERROR 시 배열)")


class ErrorResponseSchema(CamelModel):
    """실패 응답 스키마"""
    success: bool = Field(default=False, description="성공 여부 (항상 false)", examples=[False])
    error: ErrorDetailSchema = Field(description="에러 상세 정보")
