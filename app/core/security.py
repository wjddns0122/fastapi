from __future__ import annotations

import base64
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import json
import secrets
from typing import Any

from app.core.config import settings
from app.core.exceptions import AppException


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    )
    return f"{salt}${hashed.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        salt, stored_hash = hashed_password.split("$", maxsplit=1)
    except ValueError:
        return False
    candidate_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    )
    return secrets.compare_digest(candidate_hash.hex(), stored_hash)


def create_access_token(subject: str) -> str:
    return _encode_token(
        payload={"sub": subject, "type": "access"},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(subject: str) -> str:
    return _encode_token(
        payload={"sub": subject, "type": "refresh"},
        expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes),
    )


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
    except ValueError as exc:
        raise AppException(
            code="UNAUTHORIZED",
            message="유효하지 않은 토큰입니다.",
            status_code=401,
        ) from exc

    expected_signature = _sign(f"{header_segment}.{payload_segment}")
    if not secrets.compare_digest(expected_signature, signature_segment):
        raise AppException(code="UNAUTHORIZED", message="유효하지 않은 토큰입니다.", status_code=401)

    payload_bytes = _urlsafe_b64decode(payload_segment)
    payload = json.loads(payload_bytes.decode("utf-8"))

    expires_at = payload.get("exp")
    if expires_at is None or datetime.now(UTC).timestamp() > expires_at:
        raise AppException(code="UNAUTHORIZED", message="토큰이 만료되었습니다.", status_code=401)

    if payload.get("type") != expected_type:
        raise AppException(code="UNAUTHORIZED", message="토큰 유형이 올바르지 않습니다.", status_code=401)

    return payload


def _encode_token(payload: dict[str, Any], expires_delta: timedelta) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    expires_at = datetime.now(UTC) + expires_delta
    body = {**payload, "exp": expires_at.timestamp()}

    header_segment = _urlsafe_b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = _urlsafe_b64encode(json.dumps(body, separators=(",", ":")).encode("utf-8"))
    signature_segment = _sign(f"{header_segment}.{payload_segment}")
    return f"{header_segment}.{payload_segment}.{signature_segment}"


def _sign(value: str) -> str:
    signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return _urlsafe_b64encode(signature)


def _urlsafe_b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")


def _urlsafe_b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")
