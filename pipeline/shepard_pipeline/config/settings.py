"""Application settings and configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Prefect Configuration
    prefect_api_url: str = Field(default="http://localhost:4200/api")
    prefect_logging_level: str = Field(default="INFO")

    # Supabase Configuration
    supabase_url: str = Field(default="http://localhost:54321")
    supabase_anon_key: str = Field(default="mock_anon_key")
    supabase_service_role_key: str = Field(default="mock_service_role_key")

    # External API Keys (mocked by default)
    openai_api_key: str = Field(default="mock_openai_key")
    voxtral_api_key: str = Field(default="mock_voxtral_key")
    mistral_api_key: str = Field(default="mock_mistral_key")

    # Pipeline Configuration
    mock_external_apis: bool = Field(default=True)
    chunk_size_minutes: int = Field(default=10, ge=1, le=30)
    default_language: str = Field(default="zh-TW")
    max_audio_duration_hours: int = Field(default=3, ge=1, le=24)

    # YouTube Service Configuration
    youtube_audio_quality: str = Field(
        default="192K", description="Audio quality for YouTube downloads"
    )
    youtube_audio_format: str = Field(
        default="mp3", description="Audio format for YouTube downloads"
    )
    youtube_max_duration_hours: int = Field(
        default=6, ge=1, le=12, description="Maximum duration for YouTube videos"
    )

    # Model Configuration
    transcription_model: str = Field(default="voxtral-v1")
    correction_model: str = Field(default="mistral-medium")
    summarization_model: str = Field(default="gpt-4")

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.mock_external_apis


# Global settings instance
settings = Settings()
