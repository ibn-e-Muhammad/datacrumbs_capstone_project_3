"""
Centralised configuration loaded from environment variables.

The .env file lives at the *project root* (one level above ``backend/``),
NOT inside the backend directory. ``python-dotenv`` is pointed there explicitly.

All secrets (API keys, service-account credentials) are read from env vars
only — never hard-coded or committed to version control.
"""

import logging
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

# backend/ directory
BACKEND_DIR = Path(__file__).resolve().parent

# Project root  (one level up from backend/)
PROJECT_ROOT = BACKEND_DIR.parent

# Persisted FAISS index location
FAISS_INDEX_DIR = BACKEND_DIR / "data" / "faiss_index"

# Company data files at project root
COMPANY_TXT_PATH = PROJECT_ROOT / "Company_sample.txt"
COMPANY_XLSX_PATH = PROJECT_ROOT / "Company_products.xlsx"

# .env file at project root
DOTENV_PATH = PROJECT_ROOT / ".env"


# ---------------------------------------------------------------------------
# Settings model
# ---------------------------------------------------------------------------

class Settings(BaseSettings):
    """Application settings populated from environment variables.

    Pydantic-settings will automatically look for a ``.env`` file at
    ``DOTENV_PATH`` and load any matching variables.
    """

    # --- Google Generative AI (Gemini) ---
    google_api_key: str = Field(
        ...,
        alias="GOOGLE_API_KEY",
        description="API key for Google Generative AI (Gemini).",
    )

    # --- Google Service Account (for Sheets) ---
    google_client_email: str = Field(
        ...,
        alias="GOOGLE_CLIENT_EMAIL",
        description="Service-account client email for Google Sheets.",
    )
    google_private_key: str = Field(
        ...,
        alias="GOOGLE_PRIVATE_KEY",
        description="Service-account private key (PEM) for Google Sheets.",
    )
    google_project_id: str = Field(
        ...,
        alias="GOOGLE_PROJECT_ID",
        description="GCP project ID associated with the service account.",
    )

    # --- Google Sheets ---
    google_sheet_id: str = Field(
        default="1GtmWcVJSNZmgbBkDbc6tZtmhs18GosdB7h6tmsLNlxk",
        alias="GOOGLE_SHEET_ID",
        description="ID of the Google Sheet containing Orders and Tickets.",
    )

    # --- Application ---
    app_env: str = Field(
        default="development",
        alias="APP_ENV",
        description="Runtime environment (development | staging | production).",
    )
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
        description="Logging verbosity level.",
    )
    cors_origins: str = Field(
        default="http://localhost:3000",
        alias="CORS_ORIGINS",
        description="Comma-separated list of allowed CORS origins.",
    )

    model_config = {
        "env_file": str(DOTENV_PATH),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "populate_by_name": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance (singleton)."""
    logger.info("Loading application settings from %s", DOTENV_PATH)
    return Settings()
