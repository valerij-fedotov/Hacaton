from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://dtp_user:dtp_pass@localhost/dtp_forms"

    class Config:
        env_file = ".env"

settings = Settings()