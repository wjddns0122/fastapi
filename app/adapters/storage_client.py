from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.core.exceptions import AppException


@dataclass(frozen=True)
class SignedUploadData:
    file_key: str
    upload_url: str
    public_url: str


class SupabaseStorageClient:
    def __init__(
        self,
        supabase_url: str | None = None,
        service_role_key: str | None = None,
        bucket_name: str | None = None,
    ) -> None:
        self.supabase_url = (supabase_url or settings.supabase_url or "").rstrip("/")
        self.service_role_key = service_role_key or settings.supabase_service_role_key
        self.bucket_name = bucket_name or settings.supabase_storage_bucket
        self._http_client = httpx.Client(timeout=settings.supabase_request_timeout_seconds)

    def close(self) -> None:
        self._http_client.close()

    def create_signed_upload_url(
        self,
        file_key: str,
        content_type: str,
        upsert: bool = True,
    ) -> SignedUploadData:
        if not self.supabase_url or not self.service_role_key:
            raise AppException(
                code="INTERNAL_SERVER_ERROR",
                message="Supabase Storage 설정이 누락되었습니다.",
                status_code=500,
            )

        endpoint = (
            f"{self.supabase_url}/storage/v1/object/upload/sign/"
            f"{self.bucket_name}/{file_key}"
        )
        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
            "x-upsert": str(upsert).lower(),
        }
        payload = {"contentType": content_type}

        response = self._http_client.post(endpoint, headers=headers, json=payload)

        if response.status_code >= 400:
            raise AppException(
                code="INTERNAL_SERVER_ERROR",
                message=self._extract_error_message(response=response),
                status_code=500,
            )

        response_body = response.json()
        return SignedUploadData(
            file_key=file_key,
            upload_url=self._build_upload_url(response_body=response_body, file_key=file_key),
            public_url=self._build_public_url(file_key=file_key),
        )

    def _build_upload_url(self, response_body: dict, file_key: str) -> str:
        relative_url = response_body.get("url")
        token = response_body.get("token")

        if relative_url:
            parsed_url = urlparse(relative_url)
            if parsed_url.scheme and parsed_url.netloc:
                return relative_url
            return f"{self.supabase_url}/storage/v1{relative_url}"

        if token:
            return (
                f"{self.supabase_url}/storage/v1/object/upload/sign/"
                f"{self.bucket_name}/{file_key}?token={token}"
            )

        raise AppException(
            code="INTERNAL_SERVER_ERROR",
            message="Supabase Storage 응답이 올바르지 않습니다.",
            status_code=500,
        )

    def _build_public_url(self, file_key: str) -> str:
        return (
            f"{self.supabase_url}/storage/v1/object/public/"
            f"{self.bucket_name}/{file_key}"
        )

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        try:
            response_body = response.json()
        except ValueError:
            return "Supabase Storage 요청에 실패했습니다."

        return (
            response_body.get("message")
            or response_body.get("error")
            or "Supabase Storage 요청에 실패했습니다."
        )
