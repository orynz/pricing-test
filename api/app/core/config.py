from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Secure Core Platform"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "replace-this-with-a-very-secure-random-string" # TODO: Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # AES Payload Encryption (for Desktop App)
    AES_SECRET_KEY: str = "32-char-long-secret-key-for-aes-256" # must be 32 bytes
    
    # Database (Supabase / PostgreSQL)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"
    
    # Supabase Settings
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    SUPABASE_PUBLIC_KEY: Optional[str] = None
    
    # Polar.sh Settings
    POLAR_API_KEY: str = ""
    POLAR_WEBHOOK_SECRET: str = ""
    POLAR_ORGANIZATION_ID: str = ""
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
