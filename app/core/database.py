"""
Database client initialization with Supabase integration.

This module manages the Supabase client for database operations.
"""

import logging
from typing import Optional, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Attempt to import Supabase, handle missing dependencies gracefully
try:
    from supabase import Client, create_client
    SUPABASE_AVAILABLE = True
except ModuleNotFoundError as e:
    logger.warning(f"Supabase not available: {e}. Database operations will fail.")
    SUPABASE_AVAILABLE = False
    Client = Any  # type: ignore
    create_client = None  # type: ignore


def _validate_supabase_credentials() -> tuple[str, str]:
    """
    Validate Supabase credentials are configured.

    Returns:
        Tuple of (supabase_url, supabase_key)

    Raises:
        ValueError: If credentials are missing or empty
    """
    url = settings.supabase_url
    key = settings.supabase_key

    if not url or not key:
        missing = []
        if not url:
            missing.append("SUPABASE_URL")
        if not key:
            missing.append("SUPABASE_KEY")
        raise ValueError(
            f"Missing required Supabase credentials: {', '.join(missing)}. "
            "Please set them in your .env file."
        )

    return url, key


def get_supabase_client() -> Client:
    """
    Get or create a Supabase client instance.

    This function validates credentials and returns a ready-to-use Supabase client.

    Returns:
        Initialized Supabase client

    Raises:
        ValueError: If Supabase credentials are not configured or Supabase is not available

    Example:
        client = get_supabase_client()
        response = await client.table("users").select("*").execute()
    """
    if not SUPABASE_AVAILABLE:
        raise RuntimeError(
            "Supabase client is not available due to missing dependencies (pyroaring). "
            "Please install the full requirements or configure Supabase properly."
        )
    
    url, key = _validate_supabase_credentials()
    return create_client(url, key)


# Lazy-loaded singleton client (initialized on first use)
_client: Optional[Client] = None


def init_supabase_client() -> Client:
    """
    Initialize the singleton Supabase client.

    Call this during application startup for eager initialization
    and early credential validation.

    Returns:
        Initialized Supabase client

    Raises:
        ValueError: If Supabase credentials are not configured
    """
    global _client
    if _client is None:
        _client = get_supabase_client()
    return _client
