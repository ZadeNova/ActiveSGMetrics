from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Strictly required
    SUPABASE_DATABASE_URL: str
    ACTIVE_SG_API: str
    
    # Optional
    SUPABASE_DEV_DATABASE_URL: Optional[str] = None
    WEBSITE_URL: Optional[str] = None
    
    LOCAL_BACKEND_URL: str = "http://localhost:8000"
    LOCAL_BACKEND_HEALTH_URL: Optional[str] = None
    
    PROD_BACKEND_URL: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
settings = Settings()