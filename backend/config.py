from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SUPABASE_DATABASE_URL: str
    ACTIVE_SG_API: str
    
    SUPABASE_DEV_DATABASE_URL: str
    WEBSITE_URL: str
    
    LOCAL_BACKEND_URL: str
    LOCAL_BACKEND_HEALTH_URL: str
    
    PROD_BACKEND_URL: str
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
settings = Settings()