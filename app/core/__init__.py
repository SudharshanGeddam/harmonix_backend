"""Core module containing configuration and database setup."""

from app.core.config import settings

try:
    from app.core.database import get_supabase_client
except Exception as e:
    import logging
    logging.warning(f"Failed to import database module: {e}")
    get_supabase_client = None  # type: ignore

__all__ = ["settings", "get_supabase_client"]
