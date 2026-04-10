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


@router.post(
    "/signup",
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
                            "user": {"id": "uuid", "email": "user@example.com", "nickname": "jfh"},
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
        }
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
    response_model=SuccessResponseSchema[UserWithTokensResponseSchema],
    responses={
        200: {
            "description": "로그인 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "user": {"id": "uuid", "email": "user@example.com", "nickname": "jfh"},
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
        }
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
        }
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
        }
    },
)
def get_me(current_user: User = Depends(get_current_user)):
    return success_response(
        data=UserProfileSchema.model_validate(current_user),
        message="OK",
    )
