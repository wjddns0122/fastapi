from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from app.api.v1.api import api_router
from app.core.db import Base, engine
from app.core.exceptions import AppException
from app.core.response import error_response, success_response
from app.models import daily_compatibility as daily_compatibility_model
from app.models import relationship as relationship_model
from app.models import relationship_activity as relationship_activity_model
from app.models import user as user_model

load_dotenv()

_DESCRIPTION = """
## 개요
사용자 인증, 프로필 관리, 사용자 간 관계(친구/연인 등) 기능을 제공하는 백엔드 API입니다.

## 인증
대부분의 엔드포인트는 `Authorization: Bearer <accessToken>` 헤더를 요구합니다.
- `/auth/signup` · `/auth/login` · `/auth/refresh` 는 인증 없이 호출 가능합니다.
- 액세스 토큰 만료 시 `/auth/refresh` 로 갱신하세요.

## 공통 응답 형식
### 성공
```json
{"success": true, "data": { ... }, "message": "OK"}
```
### 실패
```json
{"success": false, "error": {"code": "ERROR_CODE", "message": "설명"}}
```

## 에러 코드 목록
| code | HTTP | 설명 |
|------|------|------|
| `UNAUTHORIZED` | 401 | 인증 토큰 누락 또는 만료 |
| `FORBIDDEN` | 403 | 권한 없음 |
| `NOT_FOUND` | 404 | 리소스를 찾을 수 없음 |
| `CONFLICT` | 409 | 중복 요청 또는 이미 처리된 상태 |
| `BAD_REQUEST` | 400 | 잘못된 요청 (자기 자신에게 요청 등) |
| `VALIDATION_ERROR` | 422 | 요청 바디/쿼리 유효성 오류 |
"""

_OPENAPI_TAGS = [
    {
        "name": "auth",
        "description": "회원가입, 로그인, 토큰 재발급, 내 정보 조회 등 **인증 관련** 엔드포인트",
    },
    {
        "name": "users",
        "description": "프로필 수정, 프로필 이미지 업로드 URL 발급 등 **사용자 정보** 엔드포인트",
    },
    {
        "name": "relationships",
        "description": "친구/연인 요청 생성·수락·거절·삭제 및 목록 조회 등 **관계 관리** 엔드포인트",
    },
    {
        "name": "activities",
        "description": "궁합 점수에 반영되는 편지, 퀘스트, 상점, 아바타 등 **활동 이벤트 기록** 엔드포인트",
    },
    {
        "name": "compatibility",
        "description": "오늘의 궁합 조회 및 내부 재계산 등 **궁합 계산** 엔드포인트",
    },
    {
        "name": "system",
        "description": "서버 상태 확인용 **시스템** 엔드포인트",
    },
]

app = FastAPI(
    title="Backend FastAPI",
    description=_DESCRIPTION,
    version="1.0.0",
    openapi_tags=_OPENAPI_TAGS,
    contact={"name": "wjddns0122"},
    license_info={"name": "Private"},
)
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


@app.get("/", tags=["system"], summary="서비스 정보", description="서비스 이름을 반환합니다.")
def root():
    return success_response(
        data={"serviceName": "backend-fastapi"},
        message="OK",
    )


@app.get("/health", tags=["system"], summary="헬스 체크", description="서버가 정상 동작 중인지 확인합니다.")
def health():
    return success_response(
        data={"status": "healthy"},
        message="OK",
    )
