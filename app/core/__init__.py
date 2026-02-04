"""Core module containing configuration and database setup."""

from app.core.config import settings
from app.core.database import get_supabase_client

__all__ = ["settings", "get_supabase_client"]
