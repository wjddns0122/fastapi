from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from app.api.v1.api import api_router
from app.core.db import Base, engine
from app.core.exceptions import AppException
from app.core.response import error_response, success_response
from app.models import user as user_model

load_dotenv()

app = FastAPI(title="Backend FastAPI")
app.include_router(api_router)

Base.metadata.create_all(bind=engine)


@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    return error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return error_response(
        code="VALIDATION_ERROR",
        message="요청 데이터를 확인해주세요.",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details=jsonable_encoder(exc.errors()),
    )


@app.get("/")
def root():
    return success_response(
        data={"serviceName": "backend-fastapi"},
        message="OK",
    )


@app.get("/health")
def health():
    return success_response(
        data={"status": "healthy"},
        message="OK",
    )
