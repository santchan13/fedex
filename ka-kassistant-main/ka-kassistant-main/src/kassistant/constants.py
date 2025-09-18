"""
Loads configuration from environment variables and `.env` files.

By default, the values defined in the classes are used.
They can be overridden by an env var with the same name.

An `.env` file is used to populate env vars, if present.
"""

from os import getenv
from typing import Final

from pydantic_settings import BaseSettings

GIT_SHA: Final[str] = getenv("GIT_SHA", "development")


class EnvConfig(
    BaseSettings,
    env_file="kerp-shipping.env",
    env_file_encoding="utf-8",
    env_nested_delimiter="__",
    extra="ignore",
):
    """Our default configuration for models that should load from .env files."""


class _App(EnvConfig, env_prefix="app_"):
    """App config."""

    database_url: str = "postgresql+psycopg://postgres:shadow@postgres17/kassistant"
    time_zone: str = "America/Chicago"


App = _App()


class _KERP(EnvConfig, env_prefix="kerp_"):
    """K-ERP connection details."""

    api_key: str = ""


KERP = _KERP()


class _FedEx(EnvConfig, env_prefix="fedex_"):
    """FedEx connection details."""

    base_url: str = "https://apis.fedex.com"
    client_id: str = ""
    client_secret: str = ""
    account: str = ""


FedEx = _FedEx()


class _Sentry(EnvConfig, env_prefix="sentry_"):
    """Environment variables for Sentry."""

    dsn: str = ""
    release_prefix: str = "kassistant"
    environment: str = "production"


Sentry = _Sentry()
