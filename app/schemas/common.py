from app.schemas.base import CamelModel
from typing import Any, Generic, TypeVar
from pydantic import Field

T = TypeVar("T")

class SuccessResponseSchema(CamelModel, Generic[T]):
    """성공 응답 스키마"""
    success: bool = Field(default=True, description="성공 여부", examples=[True])
    data: T = Field(description="응답 데이터")
    message: str = Field(default="OK", description="응답 메시지", examples=["OK"])


class ErrorDetailSchema(CamelModel):
    code: str
    message: str
    details: Any | None = None


class ErrorResponseSchema(CamelModel):
    success: bool = False
    error: ErrorDetailSchema
