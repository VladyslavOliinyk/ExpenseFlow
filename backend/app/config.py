from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    ai_mode: str = "mock"  # mock | auto
    anthropic_api_key: str = ""
    google_ai_api_key: str = ""
    ai_timeout_seconds: int = 5

    environment: str = "development"
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


settings = Settings()
