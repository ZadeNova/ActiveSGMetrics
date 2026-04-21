from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from typing import Optional

class Settings(BaseSettings):
    # Strictly required
    SUPABASE_DATABASE_URL: str
    ACTIVE_SG_API: str
    
    # Optional
    SUPABASE_DEV_DATABASE_URL: Optional[str] = None
    WEBSITE_URL: Optional[str] = None
    
    @computed_field
    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        if self.WEBSITE_URL is None:
            return ["http://localhost:3000"]
        else:
            return [self.WEBSITE_URL, "http://localhost:3000"]
    
    LOCAL_BACKEND_URL: str = "http://localhost:8000"
    LOCAL_BACKEND_HEALTH_URL: Optional[str] = None
    
    PROD_BACKEND_URL: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
settings = Settings()