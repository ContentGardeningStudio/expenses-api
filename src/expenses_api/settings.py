from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./expenses.db"
    DEBUG: bool = True

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
