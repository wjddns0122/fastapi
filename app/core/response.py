from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.schemas.common import ErrorDetailSchema, ErrorResponseSchema, SuccessResponseSchema


def success_response(
    data: Any,
    message: str = "OK",
    status_code: int = 200,
) -> JSONResponse:
    payload = SuccessResponseSchema(data=data, message=message)
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(payload, by_alias=True),
    )


def error_response(
    code: str,
    message: str,
    status_code: int,
    details: Any | None = None,
) -> JSONResponse:
    payload = ErrorResponseSchema(
        error=ErrorDetailSchema(
            code=code,
            message=message,
            details=details,
        ),
    )
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(payload, by_alias=True, exclude_none=True),
    )
