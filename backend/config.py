from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from typing import Optional

class Settings(BaseSettings):
    # Strictly required
    DATABASE_URL: str

    # Optional
    WEBSITE_URL: Optional[str] = None
    
    @computed_field
    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        if self.WEBSITE_URL is None:
            return ["http://localhost:3000"]
        else:
            return [self.WEBSITE_URL, "http://localhost:3000"]
    
    # Failure-only email alert for the scraper, sent via Gmail SMTP.
    # Optional so local runs without alerting configured still work.
    ALERT_EMAIL_FROM: Optional[str] = None
    ALERT_EMAIL_TO: Optional[str] = None
    ALERT_EMAIL_APP_PASSWORD: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
settings = Settings()