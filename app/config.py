"""Centralized configuration for AgriLedger.

Loads environment variables from .env and provides validation.
Required variables fail fast when running in production (APP_ENV=production).
"""

import logging
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _is_production() -> bool:
    return os.getenv("APP_ENV", "development").lower() == "production"


def _get_env(key: str, default: str = "", required: bool = False) -> str:
    """Get an environment variable; required vars fail fast in production."""
    value = os.getenv(key, default)
    if required and not value:
        if _is_production():
            raise RuntimeError(f"Required environment variable '{key}' is not set.")
        logger.warning(f"Required environment variable '{key}' is not set.")
    return value


def _load_secret_key() -> str:
    value = os.getenv("SECRET_KEY")
    if value:
        return value
    if _is_production():
        raise RuntimeError("SECRET_KEY must be set when APP_ENV=production.")
    return "dev-secret-change-in-production"


def _load_cors_origins() -> tuple[str, ...]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
    return tuple(origin.strip() for origin in raw.split(",") if origin.strip())


@dataclass(frozen=True)
class MongoDBConfig:
    uri: str = field(default_factory=lambda: _get_env("MONGODB_URI", "mongodb://localhost:27017/agriledger_db"))
    database_name: str = field(default_factory=lambda: _get_env("MONGODB_DATABASE", "agriledger"))


# Ordered fallbacks tried when the configured Gemini model is deprecated,
# blocked for the API key, or otherwise unavailable (in priority order).
# gemini-1.5-flash / 2.x are retired for new keys, so fallbacks are 3.x models
# verified to accept both text and vision (OCR) calls.
GEMINI_MODEL_FALLBACKS = (
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
)


@dataclass(frozen=True)
class GeminiConfig:
    api_key: str = field(default_factory=lambda: _get_env("GEMINI_API_KEY"))
    # gemini-1.5-flash is deprecated/blocked for new keys; default to a
    # modern, widely-available model (override via GEMINI_MODEL in .env).
    model: str = field(default_factory=lambda: _get_env("GEMINI_MODEL", "gemini-3.1-flash-lite"))

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    @property
    def model_candidates(self) -> list[str]:
        """Configured model first, then deduplicated fallbacks.

        Lets callers fail over automatically when the configured model is
        deprecated or unavailable for a given API key.
        """
        candidates = [self.model]
        for model in GEMINI_MODEL_FALLBACKS:
            if model not in candidates:
                candidates.append(model)
        return candidates


@dataclass(frozen=True)
class ResendConfig:
    api_key: str = field(default_factory=lambda: _get_env("RESEND_API_KEY"))
    from_email: str = field(default_factory=lambda: _get_env("RESEND_FROM_EMAIL", "noreply@agriledger.com"))

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)


@dataclass(frozen=True)
class TwilioConfig:
    account_sid: str = field(default_factory=lambda: _get_env("TWILIO_ACCOUNT_SID"))
    auth_token: str = field(default_factory=lambda: _get_env("TWILIO_AUTH_TOKEN"))
    phone_number: str = field(default_factory=lambda: _get_env("TWILIO_PHONE_NUMBER"))

    @property
    def is_configured(self) -> bool:
        return bool(self.account_sid and self.auth_token and self.phone_number)


@dataclass(frozen=True)
class AppConfig:
    mongodb: MongoDBConfig = field(default_factory=MongoDBConfig)
    gemini: GeminiConfig = field(default_factory=GeminiConfig)
    resend: ResendConfig = field(default_factory=ResendConfig)
    twilio: TwilioConfig = field(default_factory=TwilioConfig)
    secret_key: str = field(default_factory=_load_secret_key)
    debug: bool = field(default_factory=lambda: _get_env("DEBUG", "false").lower() in ("true", "1", "yes"))
    app_env: str = field(default_factory=lambda: _get_env("APP_ENV", "development").lower())
    trust_proxy: bool = field(default_factory=lambda: _get_env("TRUST_PROXY", "false").lower() in ("true", "1", "yes"))
    cors_origins: tuple[str, ...] = field(default_factory=_load_cors_origins)
    rate_limit_max_requests: int = field(default_factory=lambda: int(_get_env("RATE_LIMIT_MAX_REQUESTS", "60")))
    rate_limit_window_seconds: int = field(default_factory=lambda: int(_get_env("RATE_LIMIT_WINDOW_SECONDS", "60")))
    token_expiry_seconds: int = field(default_factory=lambda: int(_get_env("TOKEN_EXPIRY_SECONDS", "86400")))


# Global config singleton
config = AppConfig()
