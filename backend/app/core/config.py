"""
Application configuration loaded from environment variables or a .env file.

Owner: Member 3 (backend core).
All settings are centralised here; modules import `get_settings()` and never
read `os.environ` directly.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Runtime configuration for the CLOUDSHIELD backend.

    All fields can be overridden via environment variables or a .env file
    placed next to the process working directory.  See .env.example for
    documentation of every variable.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ------------------------------------------------------------------ #
    # Application identity
    # ------------------------------------------------------------------ #
    APP_NAME: str = "CLOUDSHIELD Backend"
    APP_ENV: str = "development"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"

    # ------------------------------------------------------------------ #
    # Database
    # ------------------------------------------------------------------ #
    DATABASE_URL: str = "sqlite:///./data/app.db"

    # ------------------------------------------------------------------ #
    # Logging
    # ------------------------------------------------------------------ #
    LOG_LEVEL: str = "INFO"

    # ------------------------------------------------------------------ #
    # Pipeline
    # ------------------------------------------------------------------ #
    # Keep false by default so the server boots without module stubs failing.
    PIPELINE_ENABLED: bool = False
    WINDOW_SECONDS: int = Field(default=10, ge=1)

    # ------------------------------------------------------------------ #
    # Nginx integration
    # ------------------------------------------------------------------ #
    NGINX_ACCESS_LOG_PATH: str = "/var/log/nginx/access.log"
    NGINX_BLOCKLIST_PATH: str = "/etc/nginx/conf.d/blocklist.conf"

    # ------------------------------------------------------------------ #
    # Replica health
    # ------------------------------------------------------------------ #
    # Comma-separated list; parsed into a Python list by the validator below.
    REPLICA_URLS: str = "http://app1:8080,http://app2:8080"
    HEALTH_CHECK_INTERVAL_S: int = Field(default=10, ge=1)

    # ------------------------------------------------------------------ #
    # Mitigation
    # ------------------------------------------------------------------ #
    MITIGATION_DEFAULT_TTL_S: int = Field(default=300, ge=1)

    # ------------------------------------------------------------------ #
    # Risk thresholds — placeholder values, to be tuned by Member 2.
    # ------------------------------------------------------------------ #
    RISK_MEDIUM_MIN: Annotated[int, Field(ge=0, le=100)] = 30
    RISK_HIGH_MIN: Annotated[int, Field(ge=0, le=100)] = 60
    RISK_CRITICAL_MIN: Annotated[int, Field(ge=0, le=100)] = 85

    # ------------------------------------------------------------------ #
    # ML detector
    # ------------------------------------------------------------------ #
    ML_DETECTOR_ENABLED: bool = False

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    @property
    def replica_url_list(self) -> list[str]:
        """Return REPLICA_URLS as a list of stripped URL strings."""
        return [u.strip() for u in self.REPLICA_URLS.split(",") if u.strip()]

    @field_validator("LOG_LEVEL")
    @classmethod
    def _validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return upper

    @field_validator("APP_ENV")
    @classmethod
    def _validate_app_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        lower = v.lower()
        if lower not in allowed:
            raise ValueError(f"APP_ENV must be one of {allowed}")
        return lower


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the cached application settings singleton.

    Use this in FastAPI dependency injection::

        from app.core.config import get_settings
        settings = Depends(get_settings)
    """
    return Settings()
