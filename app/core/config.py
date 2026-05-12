from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    secret_key: str = os.getenv("SECRET_KEY", "development-secret-key")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"),
    )
    refresh_token_expire_minutes: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 14)),
    )
    supabase_url: str | None = os.getenv("SUPABASE_URL")
    supabase_service_role_key: str | None = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase_storage_bucket: str = os.getenv("SUPABASE_STORAGE_BUCKET", "fastapi")
    supabase_request_timeout_seconds: float = float(
        os.getenv("SUPABASE_REQUEST_TIMEOUT_SECONDS", "10"),
    )
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini_request_timeout_seconds: float = float(
        os.getenv("GEMINI_REQUEST_TIMEOUT_SECONDS", "10"),
    )
    internal_secret: str | None = os.getenv("INTERNAL_SECRET")
    compatibility_refresh_token: str | None = os.getenv(
        "COMPATIBILITY_REFRESH_TOKEN",
    )


settings = Settings()
