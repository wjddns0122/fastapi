from typing import Any

from app.schemas.base import CamelModel


class SuccessResponseSchema(CamelModel):
    success: bool = True
    data: Any
    message: str = "OK"


class ErrorDetailSchema(CamelModel):
    code: str
    message: str
    details: Any | None = None


class ErrorResponseSchema(CamelModel):
    success: bool = False
    error: ErrorDetailSchema
