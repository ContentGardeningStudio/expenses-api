from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field, SecretStr


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./expenses.db"
    DEBUG: bool = True

    SECRET_KEY: SecretStr = Field(default="secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = ConfigDict(env_file=".env", extra="ignore")


settings = Settings()
