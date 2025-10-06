# src/core/config.py
from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API / Integración
    SCHEME: Literal["http", "https"] = Field(default="http")
    HOST: str = Field(...)
    PORT: int = Field(...)
    BASE_PATH: str = Field(...)
    AUTH_TYPE: str = "Basic"
    AUTH_TOKEN: str = Field(...)

    FUNDO: str = Field(...)
    CULTIVO: str = Field(...)
    RUC_EMPRESA: str = Field(...)

    CARTILLA_PIQUILLO: str = Field(...)
    CARTILLA_CALIFORNIA: str = Field(...)
    CARTILLA_CONTEOS_PIQUILLO: str = Field(...)
    CARTILLA_CONTEOS_CALIFORNIA: str = Field(...)

    # DB
    RAW_STORAGE_HOST: str = "localhost"
    RAW_STORAGE_PORT: int = 5432
    RAW_STORAGE_USER: str = "postgres"
    RAW_STORAGE_PASSWORD: str = Field(...)
    RAW_STORAGE_DATABASE: str = "peppers_raw"

    # **Nuevo**: echo de SQLAlchemy
    DB_ECHO_LOG: bool = True

    # Derivados
    @computed_field
    @property
    def API_BASE_URL(self) -> str:
        base_path = (
            self.BASE_PATH if self.BASE_PATH.startswith("/") else f"/{self.BASE_PATH}"
        )
        return f"{self.SCHEME}://{self.HOST}:{self.PORT}{base_path.rstrip('/') or '/'}"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        user = quote_plus(self.RAW_STORAGE_USER)
        pwd = quote_plus(self.RAW_STORAGE_PASSWORD)
        return f"postgresql+asyncpg://{user}:{pwd}@{self.RAW_STORAGE_HOST}:{self.RAW_STORAGE_PORT}/{self.RAW_STORAGE_DATABASE}"

    # Alias en minúsculas para compatibilidad con tu engine actual
    @computed_field
    @property
    def database_url(self) -> str:
        return self.DATABASE_URL

    @field_validator("PORT", "RAW_STORAGE_PORT")
    @classmethod
    def _validate_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


# **Exporta** una instancia para `from src.core.config import settings`
settings: Settings = get_settings()
