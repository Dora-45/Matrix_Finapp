from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "finapp.db"


class Settings(BaseSettings):
    app_name: str = "ФинАналитика API"
    app_version: str = "0.1.0"
    debug: bool = True
    database_url: str = f"sqlite:///{DB_PATH.as_posix()}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()