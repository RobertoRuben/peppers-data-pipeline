from functools import lru_cache
from typing import Annotated
from pydantic import Field, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings using Pydantic v2 BaseSettings for validation and type safety."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Configuration
    scheme: str = Field(default="http", description="API scheme (http/https)")
    host: str = Field(..., description="API host")
    port: Annotated[str, Field(..., description="API port")] 
    base_path: str = Field(..., description="API base path")
    auth_type: str = Field(default="Basic", description="Authentication type")
    auth_token: str = Field(..., description="Authentication token")
    fundo: str = Field(..., description="Fundo identifier")
    cultivo: str = Field(..., description="Cultivo identifier")
    ruc_empresa: str = Field(..., description="RUC empresa")
    
    # Cartilla Configuration
    cartilla_piquillo: str = Field(..., description="Cartilla proyección piquillo")
    cartilla_california: str = Field(..., description="Cartilla proyección california")
    cartilla_conteos_piquillo: str = Field(..., description="Cartilla conteos piquillo")
    cartilla_conteos_california: str = Field(..., description="Cartilla conteos california")
    
    # Database Configuration
    raw_storage_host: str = Field(default="localhost", description="Database host")
    raw_storage_port: Annotated[str, Field(default="5432", description="Database port")]
    raw_storage_user: str = Field(default="postgres", description="Database user")
    raw_storage_password: str = Field(..., description="Database password")
    raw_storage_database: str = Field(default="peppers_raw", description="Database name")

    @computed_field
    @property
    def database_url(self) -> str:
        """Generate the async PostgreSQL database URL."""
        return (
            f"postgresql+asyncpg://{self.raw_storage_user}:{self.raw_storage_password}"
            f"@{self.raw_storage_host}:{self.raw_storage_port}/{self.raw_storage_database}"
        )

    @field_validator("port", "raw_storage_port")
    @classmethod
    def validate_port(cls, v: str) -> str:
        """Validate that port is a valid port number."""
        try:
            port_int = int(v)
            if not (1 <= port_int <= 65535):
                raise ValueError("Port must be between 1 and 65535")
            return v
        except ValueError as e:
            raise ValueError("Port must be a valid integer") from e

    @field_validator("scheme")
    @classmethod
    def validate_scheme(cls, v: str) -> str:
        """Validate that scheme is http or https."""
        if v.lower() not in ["http", "https"]:
            raise ValueError("Scheme must be 'http' or 'https'")
        return v.lower()


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance.
    
    Using lru_cache ensures we only create one instance and reuse it,
    which is more efficient than the previous singleton pattern.
    """
    return Settings()
