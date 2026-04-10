from app.schemas.base import CamelModel
from typing import Any, Generic, TypeVar
from pydantic import Field

T = TypeVar("T")

class SuccessResponseSchema(CamelModel, Generic[T]):
    success: bool = Field(default=True, examples=[True])
    data: T
    message: str = Field(default="OK", examples=["OK"])


class ErrorDetailSchema(CamelModel):
    code: str
    message: str
    details: Any | None = None


class ErrorResponseSchema(CamelModel):
    success: bool = False
    error: ErrorDetailSchema
