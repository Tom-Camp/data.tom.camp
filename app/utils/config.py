from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ADMIN_SECRET_KEY: SecretStr = Field(description="Admin secret key")
    APP_NAME: str = Field(default="Tom.Camp.Api")
    CORS_ORIGINS: list[str] = []
    ENVIRONMENT: str | None = None
    HASH_ALGORITHM: str = Field(default="blake2b", description="Hash algorithm")
    HASH_SALT: SecretStr = Field(description="Hash salt")
    LOG_LEVEL: str = Field(default="INFO")
    LOG_NAME: str | None = Field(default=None)
    LOG_JSON_FORMAT: bool = False
    POSTGRES_DB: str = Field(description="PostgreSQL database name")
    POSTGRES_HOST: str = Field(description="PostgreSQL host")
    POSTGRES_PASS: SecretStr = Field(
        validation_alias=AliasChoices("POSTGRES_PASS", "postgres_password"),
        description="PostgreSQL password",
    )
    POSTGRES_PORT: int = Field(description="PostgreSQL port")
    POSTGRES_USER: str = Field(description="PostgreSQL user")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def async_database_url(self) -> str:
        pwd = self.POSTGRES_PASS.get_secret_value()
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{pwd}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
