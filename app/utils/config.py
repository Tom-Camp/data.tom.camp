from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ADMIN_SECRET_KEY: str = Field(description="Admin secret key")
    APP_NAME: str = Field(default="Tom.Camp.Api")
    CORS_ORIGINS: list[str] | None = None
    ENVIRONMENT: str | None = None
    HASH_ALGORITHM: str | None = None
    LOG_LEVEL: str = Field(default="INFO")
    LOG_NAME: str = Field(default="tcdata")
    LOG_JSON_FORMAT: bool = False
    POSTGRES_DB: str | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PASS: SecretStr = Field(
        default="postgres",
        validation_alias=AliasChoices("POSTGRES_PASS", "postgres_password"),
    )
    POSTGRES_PORT: str | None = None
    POSTGRES_USER: str | None = None
    SECRET_KEY: str = Field(description="Application secret key")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @property
    def async_database_url(self) -> str:
        pwd = self.POSTGRES_PASS.get_secret_value()
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{pwd}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
