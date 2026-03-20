# src/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # 1. Tell it to load .env automatically
    model_config = SettingsConfigDict(
        env_file=".env",              # looks for .env in current working dir
        env_file_encoding="utf-8",    # good practice
        case_sensitive=False,         # env vars usually uppercase anyway
        extra="ignore",               # ignore unknown env vars (safer in prod)
    )

    # Basic fields with defaults
    environment: str = "development"
    project_name: str = "Task Workspace Manager"
    api_v1_str: str = "/api/v1"

    # Security
    secret_key: str
    access_token_expire_minutes: int = 30

    # Database (we'll compose the full URL next)
    postgres_server: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str
    postgres_db: str = "task_manager_dev"



    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_server}:{self.postgres_port}/"
            f"{self.postgres_db}"

        )

@lru_cache
def get_settings() -> Settings:
    return Settings() 

settings = get_settings()
