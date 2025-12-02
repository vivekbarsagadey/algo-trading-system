import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "algo_trading"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    # Optional full database url (e.g. DATABASE_URL)
    database_url_env: Optional[str] = None

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    # Optional full redis url (e.g. REDIS_URL)
    redis_url_env: Optional[str] = None

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Broker
    broker_api_key: str = ""
    broker_api_secret: str = ""

    @property
    def database_url(self) -> str:
        # Prefer a full DATABASE_URL if provided
        # If a DATABASE_URL env var was set, prefer that
        db = os.getenv("DATABASE_URL")
        if db is not None:
            return db
        if self.database_url_env:
            return self.database_url_env
        user = self.postgres_user
        pwd = self.postgres_password
        host = self.postgres_host
        port = self.postgres_port
        db = self.postgres_db
        return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"

    @property
    def redis_url(self) -> str:
        # If REDIS_URL is provided, use it directly
        redis = os.getenv("REDIS_URL")
        if redis is not None:
            return redis
        if self.redis_url_env:
            return self.redis_url_env
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:" f"{self.redis_port}/0"
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
