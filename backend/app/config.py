from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./valet_scheduler.db"
    BOT_TOKEN: str = ""
    WEB_PASSWORD: str = "Valet2026!"
    API_BASE_URL: str = "http://localhost:8000"
    MIN_REST_HOURS: int = 10
    MAX_WEEKLY_HOURS: int = 48

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
