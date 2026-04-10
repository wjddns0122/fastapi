from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service, get_current_user
from app.core.response import success_response
from app.models.user import User
from app.schemas.auth import (
    AuthTokensSchema,
    LoginRequestSchema,
    RefreshTokenRequestSchema,
    RefreshTokenResponseSchema,
    SignUpRequestSchema,
    UserWithTokensResponseSchema,
)
from app.schemas.common import SuccessResponseSchema
from app.schemas.user import UserProfileSchema
from app.services.auth_service import AuthService

router = APIRouter()

_401 = {
    "description": "인증 실패",
    "content": {
        "application/json": {
            "example": {"success": False, "error": {"code": "UNAUTHORIZED", "message": "인증이 필요합니다."}}
        }
    },
}
_409 = {
    "description": "이미 사용 중인 이메일",
    "content": {
        "application/json": {
            "example": {"success": False, "error": {"code": "CONFLICT", "message": "이미 사용 중인 이메일입니다."}}
        }
    },
}
_422 = {
    "description": "요청 데이터 유효성 오류",
    "content": {
        "application/json": {
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "요청 데이터를 확인해주세요.",
                    "details": [{"loc": ["body", "email"], "msg": "value is not a valid email address", "type": "value_error.email"}],
                },
            }
        }
    },
}


@router.post(
    "/signup",
    summary="회원가입",
    description=(
        "새로운 사용자를 등록합니다.\n\n"
        "- 이메일은 유효한 형식이어야 하며, 중복 등록은 허용되지 않습니다.\n"
        "- 비밀번호는 8자 이상 128자 이하여야 합니다.\n"
        "- 닉네임은 2자 이상 30자 이하여야 합니다.\n"
        "- 성공 시 사용자 정보와 액세스/리프레시 토큰을 함께 반환합니다."
    ),
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseSchema[UserWithTokensResponseSchema],
    responses={
        201: {
            "description": "회원가입 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "user": {"id": "uuid", "email": "user@example.com", "nickname": "jfh", "profileImageUrl": None},
                            "tokens": {
                                "accessToken": "jwt-access-token",
                                "refreshToken": "jwt-refresh-token",
                                "tokenType": "bearer",
                            },
                        },
                        "message": "회원가입이 완료되었습니다.",
                    }
                }
            },
        },
        409: _409,
        422: _422,
    },
)
def signup(
    request: SignUpRequestSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    user, tokens = auth_service.signup(
        email=request.email,
        password=request.password,
        nickname=request.nickname,
    )
    response_data = UserWithTokensResponseSchema(
        user=UserProfileSchema.model_validate(user),
        tokens=AuthTokensSchema.model_validate(tokens),
    )
    return success_response(
        data=response_data,
        message="회원가입이 완료되었습니다.",
        status_code=status.HTTP_201_CREATED,
    )


@router.post(
    "/login",
    summary="로그인",
    description=(
        "이메일과 비밀번호로 로그인하여 JWT 토큰을 발급받습니다.\n\n"
        "- 이메일 또는 비밀번호가 틀릴 경우 401을 반환합니다.\n"
        "- 성공 시 사용자 정보와 액세스/리프레시 토큰을 함께 반환합니다."
    ),
    response_model=SuccessResponseSchema[UserWithTokensResponseSchema],
    responses={
        200: {
            "description": "로그인 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "user": {"id": "uuid", "email": "user@example.com", "nickname": "jfh", "profileImageUrl": None},
                            "tokens": {
                                "accessToken": "jwt-access-token",
                                "refreshToken": "jwt-refresh-token",
                                "tokenType": "bearer",
                            },
                        },
                        "message": "로그인되었습니다.",
                    }
                }
            },
        },
        401: {
            "description": "이메일 또는 비밀번호 불일치",
            "content": {
                "application/json": {
                    "example": {"success": False, "error": {"code": "UNAUTHORIZED", "message": "이메일 또는 비밀번호가 올바르지 않습니다."}}
                }
            },
        },
        422: _422,
    },
)
def login(
    request: LoginRequestSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    user, tokens = auth_service.login(
        email=request.email,
        password=request.password,
    )
    response_data = UserWithTokensResponseSchema(
        user=UserProfileSchema.model_validate(user),
        tokens=AuthTokensSchema.model_validate(tokens),
    )
    return success_response(
        data=response_data,
        message="로그인되었습니다.",
    )


@router.post(
    "/refresh",
    summary="액세스 토큰 재발급",
    description=(
        "만료된 액세스 토큰을 갱신합니다.\n\n"
        "- 유효한 리프레시 토큰이 필요합니다.\n"
        "- 리프레시 토큰이 만료되었거나 유효하지 않으면 401을 반환합니다.\n"
        "- 새로운 액세스 토큰과 토큰 타입을 반환합니다."
    ),
    response_model=SuccessResponseSchema[RefreshTokenResponseSchema],
    responses={
        200: {
            "description": "토큰 재발급 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "accessToken": "new-access-token",
                            "tokenType": "bearer",
                        },
                        "message": "토큰이 재발급되었습니다.",
                    }
                }
            },
        },
        401: {
            "description": "리프레시 토큰이 유효하지 않거나 만료됨",
            "content": {
                "application/json": {
                    "example": {"success": False, "error": {"code": "UNAUTHORIZED", "message": "유효하지 않은 토큰입니다."}}
                }
            },
        },
        422: _422,
    },
)
def refresh_token(
    request: RefreshTokenRequestSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    token_data = auth_service.refresh_access_token(refresh_token=request.refresh_token)
    response_data = RefreshTokenResponseSchema.model_validate(token_data)
    return success_response(
        data=response_data,
        message="토큰이 재발급되었습니다.",
    )


@router.get(
    "/me",
    summary="내 정보 조회",
    description=(
        "현재 로그인한 사용자의 프로필 정보를 조회합니다.\n\n"
        "- `Authorization: Bearer <accessToken>` 헤더가 필요합니다.\n"
        "- 토큰이 없거나 만료된 경우 401을 반환합니다."
    ),
    response_model=SuccessResponseSchema[UserProfileSchema],
    responses={
        200: {
            "description": "내 정보 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "uuid",
                            "email": "user@example.com",
                            "nickname": "jfh",
                            "profileImageUrl": "https://cdn.example.com/profiles/1.png",
                        },
                        "message": "OK",
                    }
                }
            },
        },
        401: _401,
    },
)
def get_me(current_user: User = Depends(get_current_user)):
    return success_response(
        data=UserProfileSchema.model_validate(current_user),
        message="OK",
    )
