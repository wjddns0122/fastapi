from fastapi import APIRouter, Depends, Query, status

from app.adapters.storage_client import SupabaseStorageClient
from app.api.deps import get_current_user, get_letter_service, get_storage_client
from app.core.response import success_response
from app.models.user import User
from app.schemas.common import SuccessResponseSchema
from app.schemas.letter import (
    CreateLetterRequestSchema,
    LetterAttachmentPresignRequestSchema,
    LetterAttachmentPresignResponseSchema,
    LetterCreateResponseSchema,
    LetterResponseSchema,
)
from app.services.letter_service import LetterService

router = APIRouter()


@router.post(
    "",
    response_model=SuccessResponseSchema[LetterCreateResponseSchema],
    status_code=status.HTTP_201_CREATED,
    summary="편지 작성",
)
def create_letter(
    request: CreateLetterRequestSchema,
    current_user: User = Depends(get_current_user),
    letter_service: LetterService = Depends(get_letter_service),
):
    letter = letter_service.create_letter(
        current_user=current_user,
        relationship_id=request.relationship_id,
        receiver_user_id=request.receiver_user_id,
        content=request.content,
        letter_type=request.letter_type,
        scheduled_at=request.scheduled_at,
    )
    return success_response(
        data=LetterCreateResponseSchema.model_validate(letter),
        message="편지가 저장되었습니다.",
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "",
    response_model=SuccessResponseSchema[list[LetterResponseSchema]],
    summary="내 편지 목록 조회",
)
def list_letters(
    relationship_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    letter_service: LetterService = Depends(get_letter_service),
):
    letters = letter_service.list_letters(
        current_user=current_user,
        relationship_id=relationship_id,
        status=status,
        page=page,
        size=size,
    )
    return success_response(
        data=[LetterResponseSchema.model_validate(letter) for letter in letters],
        message="OK",
    )


@router.get(
    "/{letter_id}",
    response_model=SuccessResponseSchema[LetterResponseSchema],
    summary="편지 상세 조회",
)
def get_letter(
    letter_id: str,
    current_user: User = Depends(get_current_user),
    letter_service: LetterService = Depends(get_letter_service),
):
    letter = letter_service.get_letter(
        current_user=current_user,
        letter_id=letter_id,
    )
    return success_response(
        data=LetterResponseSchema.model_validate(letter),
        message="OK",
    )


@router.post(
    "/{letter_id}/attachments/presign",
    response_model=SuccessResponseSchema[LetterAttachmentPresignResponseSchema],
    summary="편지 첨부 이미지 업로드 URL 발급",
)
def create_letter_attachment_presign(
    letter_id: str,
    request: LetterAttachmentPresignRequestSchema,
    current_user: User = Depends(get_current_user),
    letter_service: LetterService = Depends(get_letter_service),
    storage_client: SupabaseStorageClient = Depends(get_storage_client),
):
    signed_upload_data = letter_service.create_attachment_upload(
        current_user=current_user,
        letter_id=letter_id,
        file_name=request.file_name,
        content_type=request.content_type,
        storage_client=storage_client,
    )
    return success_response(
        data=LetterAttachmentPresignResponseSchema.model_validate(signed_upload_data),
        message="업로드 URL이 발급되었습니다.",
    )
