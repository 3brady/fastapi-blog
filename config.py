from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str

    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    max_upload_size_bytes: int = 5 * 1024 * 1024  # 5 MB

    posts_per_page: int = 10

    reset_token_expire_minutes: int = 60  # minutes

    resend_api_key: SecretStr = SecretStr("")
    resend_from: str = "onboarding@resend.dev"

    frontend_url: str = "http://localhost:8000"


settings = Settings()  # type: ignore[call-args]  # Loaded from .env file
