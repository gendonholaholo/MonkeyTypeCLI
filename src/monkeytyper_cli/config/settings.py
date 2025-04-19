from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application configuration settings loaded from .env file."""

    monkeytype_ape_key: str | None = None

    log_level: str = "INFO"

    api_base_url: str = "https://api.monkeytype.com"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding='utf-8',
        extra='ignore'  # Ignore extra fields from .env
    )


settings = Settings() 
