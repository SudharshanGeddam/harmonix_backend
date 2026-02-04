"""
Configuration management using Pydantic BaseSettings.

This module handles environment variables and application settings.
Load environment variables from .env file using python-dotenv.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables are loaded from .env file automatically.
    """

    # Application environment
    env: str = "development"

    # Supabase configuration (prepare for future integration)
    supabase_url: str = ""
    supabase_key: str = ""

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
