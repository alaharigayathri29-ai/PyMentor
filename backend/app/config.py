from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path
import os

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_PATH = (BACKEND_DIR / "ai_mentor.db").as_posix()


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = f"sqlite:///{DEFAULT_SQLITE_PATH}"

    # Security
    SECRET_KEY: str = "dev-secret-key-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # AI Provider
    AI_PROVIDER: str = "mock"  # mock | openai | gemini
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.5-flash"

    # Admin
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123"

    # CORS
    FRONTEND_URL: str = "*"

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_database_url(self) -> str:
        # If relative sqlite path in .env, resolve to BACKEND_DIR
        if self.DATABASE_URL.startswith("sqlite:///./"):
            rel_file = self.DATABASE_URL.replace("sqlite:///./", "")
            return f"sqlite:///{(BACKEND_DIR / rel_file).as_posix()}"
        return self.DATABASE_URL


settings = Settings()
settings.DATABASE_URL = settings.get_database_url()
