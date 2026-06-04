from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "HeyDoc API"
    app_env: Literal["local", "dev", "staging", "prod"] = "local"
    app_version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    model: str = "openai/gpt-4o-mini"
    transcribe_model: str = "google/gemini-3.1-flash-lite-preview"

    auth_required: bool = False
    auth_username: str = "admin"
    auth_password: str = "change-me"
    static_api_key: str = ""
    jwt_secret: str = "change-this-in-prod"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    max_audio_mb: int = 25
    rate_limit_per_minute: int = 120
    cache_ttl_seconds: int = 300
    rate_limit_window_seconds: int = 60

    base_url: str = Field(default="", alias="BASE_URL")
    api_key: str = Field(default="", alias="API_KEY")
    srfax_access_id: str = Field(default="", alias="SRFAX_ACCESS_ID")
    srfax_access_pwd: str = Field(default="", alias="SRFAX_ACCESS_PWD")
    srfax_url: str = Field(default="https://www.srfax.com/SRF_SecWebSvc.php", alias="SRFAX_URL")
    phaxio_api_key: str = Field(default="", alias="PHAXIO_API_KEY")
    phaxio_api_secret: str = Field(default="", alias="PHAXIO_API_SECRET")
    smtp_host: str = Field(default="smtp.gmail.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=465, alias="SMTP_PORT")
    sender_email: str = Field(default="", alias="SENDER_EMAIL")
    sender_password: str = Field(default="", alias="SENDER_PASSWORD")
    fax_retries: int = 2
    fax_retry_delay_seconds: float = 1.0
    request_timeout_seconds: int = 20
    job_timeout_seconds: int = 600

    gzip_minimum_size: int = 1024

    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    celery_broker_url: str = Field(default="", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="", alias="CELERY_RESULT_BACKEND")

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug(cls, value):
        if isinstance(value, bool):
            return value
        text = str(value or "").strip().lower()
        if text in {"1", "true", "yes", "on", "debug"}:
            return True
        if text in {"0", "false", "no", "off", "release", ""}:
            return False
        return False


@lru_cache
def get_settings() -> Settings:
    return Settings()
