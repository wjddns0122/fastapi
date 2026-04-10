from dataclasses import dataclass
import os


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


settings = Settings()
