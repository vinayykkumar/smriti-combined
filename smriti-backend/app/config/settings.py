from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smriti API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Environment
    ENVIRONMENT: str
    
    # Server
    PORT: int = 8000
    
    # Database
    MONGODB_URI: str
    DATABASE_NAME: str = "smriti"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    FIREBASE_CREDENTIALS_JSON: Optional[str] = None

    # Cron Security
    CRON_SECRET: Optional[str] = None

    # AI Provider Configuration
    AI_PROVIDER: str = "mock"  # openai | anthropic | local | mock

    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TTS_MODEL: str = "tts-1"
    OPENAI_TTS_VOICE: str = "nova"

    # Anthropic Configuration
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"

    # Local Model Configuration (Ollama)
    LOCAL_MODEL_URL: str = "http://localhost:11434"
    LOCAL_MODEL_NAME: str = "llama3"

    # Companion Rate Limits (per hour)
    COMPANION_RATE_LIMIT_PROMPT: int = 50
    COMPANION_RATE_LIMIT_CONTEMPLATE: int = 50
    COMPANION_RATE_LIMIT_MEDITATION: int = 20
    COMPANION_RATE_LIMIT_TTS: int = 50
    COMPANION_RATE_LIMIT_WINDOW: int = 3600  # 1 hour in seconds

    # Conversation History
    COMPANION_HISTORY_RETENTION_DAYS: int = 30
    COMPANION_HISTORY_MAX_ENTRIES: int = 200

    # Environment helpers
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def allowed_origins(self) -> list[str]:
        """Get CORS allowed origins based on environment"""
        if self.is_production:
            # Restrict to your actual frontend URL in production
            return [
                "https://your-app.com",  # Replace with actual domain
                "https://www.your-app.com"
            ]
        else:
            # Allow all in development
            return ["*"]
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
