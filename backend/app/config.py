from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding="utf-8")

    database_url: str
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    ai_mode: str = "mock"  # mock | auto
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"
    google_ai_api_key: str = ""
    google_ai_model: str = "gemini-2.0-flash"
    ai_timeout_seconds: int = 5

    environment: str = "development"
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


settings = Settings()
