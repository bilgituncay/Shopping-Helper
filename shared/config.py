from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    postgres_user: str = "appuser"
    postgres_password: str = "devpassword"
    postgres_db: str = "shopping_helper"
    postgres_host: str = "localhost"
    postgres_port: int = 5433

    redis_host: str = "localhost"
    redis_port: int = 6379

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

settings = Settings()