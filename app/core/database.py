"""
Database client initialization with Supabase integration.

This module manages the Supabase client for database operations.
"""

from typing import Optional

from supabase import Client, create_client

from app.core.config import settings


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
        ValueError: If Supabase credentials are not configured

    Example:
        client = get_supabase_client()
        response = await client.table("users").select("*").execute()
    """
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
