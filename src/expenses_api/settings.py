from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./expenses.db"
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
