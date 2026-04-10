from fastapi import APIRouter, Depends

from app.adapters.storage_client import SupabaseStorageClient
from app.api.deps import get_current_user, get_storage_client, get_user_service
from app.core.response import success_response
from app.models.user import User
from app.schemas.common import SuccessResponseSchema
from app.schemas.user import (
    ProfileImagePresignRequestSchema,
    ProfileImagePresignResponseSchema,
    UpdateMeRequestSchema,
    UserProfileSchema,
)
from app.services.user_service import UserService

router = APIRouter()

_401 = {
    "description": "인증 토큰 누락 또는 만료",
    "content": {
        "application/json": {
            "example": {"success": False, "error": {"code": "UNAUTHORIZED", "message": "인증이 필요합니다."}}
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
                    "details": [{"loc": ["body", "nickname"], "msg": "ensure this value has at least 2 characters", "type": "value_error.any_str.min_length"}],
                },
            }
        }
    },
}


@router.patch(
    "/me",
    summary="내 정보 수정",
    description=(
        "로그인한 사용자의 닉네임이나 프로필 이미지 URL을 수정합니다.\n\n"
        "- `nickname` 또는 `profileImageUrl` 중 하나 이상을 반드시 입력해야 합니다.\n"
        "- 닉네임은 2자 이상 30자 이하여야 합니다.\n"
        "- 프로필 이미지 URL은 최대 500자까지 허용됩니다.\n"
        "- `Authorization: Bearer <accessToken>` 헤더가 필요합니다."
    ),
    response_model=SuccessResponseSchema[UserProfileSchema],
    responses={
        200: {
            "description": "프로필 수정 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "uuid",
                            "email": "user@example.com",
                            "nickname": "new_nickname",
                            "profileImageUrl": "https://cdn.example.com/profiles/new.png",
                        },
                        "message": "프로필이 수정되었습니다.",
                    }
                }
            },
        },
        400: {
            "description": "수정할 필드가 하나도 없음",
            "content": {
                "application/json": {
                    "example": {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "수정할 필드를 하나 이상 입력해주세요."}}
                }
            },
        },
        401: _401,
        422: _422,
    },
)
def update_me(
    request: UpdateMeRequestSchema,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    updated_user = user_service.update_profile(
        user=current_user,
        nickname=request.nickname,
        profile_image_url=request.profile_image_url,
    )
    return success_response(
        data=UserProfileSchema.model_validate(updated_user),
        message="프로필이 수정되었습니다.",
    )


@router.post(
    "/me/profile-image/presign",
    summary="프로필 이미지 업로드 URL 발급",
    description=(
        "프로필 이미지를 Supabase Storage에 직접 업로드하기 위한 Signed URL을 발급합니다.\n\n"
        "**업로드 흐름:**\n"
        "1. 이 엔드포인트를 호출해 `uploadUrl`과 `publicUrl`을 받습니다.\n"
        "2. `uploadUrl`로 이미지 파일을 PUT 요청합니다.\n"
        "3. 업로드 완료 후 `publicUrl`을 `PATCH /users/me`의 `profileImageUrl`에 저장합니다.\n\n"
        "- 허용 Content-Type: `image/png`, `image/jpeg`, `image/webp`, `image/gif`\n"
        "- `Authorization: Bearer <accessToken>` 헤더가 필요합니다."
    ),
    response_model=SuccessResponseSchema[ProfileImagePresignResponseSchema],
    responses={
        200: {
            "description": "업로드 URL 발급 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "fileKey": "profiles/user-uuid/20260410-profile.png",
                            "uploadUrl": "https://s3-presigned-url",
                            "publicUrl": "https://cdn.example.com/profiles/user-uuid/20260410-profile.png",
                        },
                        "message": "업로드 URL이 발급되었습니다.",
                    }
                }
            },
        },
        400: {
            "description": "허용되지 않는 파일 타입",
            "content": {
                "application/json": {
                    "example": {"success": False, "error": {"code": "BAD_REQUEST", "message": "이미지 파일만 업로드할 수 있습니다."}}
                }
            },
        },
        401: _401,
        422: _422,
    },
)
def create_profile_image_presign(
    request: ProfileImagePresignRequestSchema,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    storage_client: SupabaseStorageClient = Depends(get_storage_client),
):
    signed_upload_data = user_service.create_profile_image_upload(
        user=current_user,
        file_name=request.file_name,
        content_type=request.content_type,
        storage_client=storage_client,
    )
    return success_response(
        data=ProfileImagePresignResponseSchema.model_validate(signed_upload_data),
        message="업로드 URL이 발급되었습니다.",
    )
