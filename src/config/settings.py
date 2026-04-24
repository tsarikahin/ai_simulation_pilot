# settings.py — Centralized user/application settings
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """Settings for LLM providers (OpenAI, Groq, etc.)"""
    openai_model: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    groq_api_key: Optional[str] = None
    groq_model: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


class APISettings(BaseSettings):
    """Settings for API server."""
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


class AppSettings(BaseSettings):
    """General application settings."""
    project_name: str = "SimCopilot"
    project_version: str = "0.1.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

class Settings(BaseSettings):
    """Aggregate settings for the entire application."""
    llm_settings: LLMSettings = Field(default_factory=LLMSettings)
    api_settings: APISettings = Field(default_factory=APISettings)
    app_settings: AppSettings = Field(default_factory=AppSettings)
    
    llm_choice: str = "groq"  # or "openai"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
