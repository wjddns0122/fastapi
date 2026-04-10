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


@router.patch(
    "/me",
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
        }
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
        }
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
