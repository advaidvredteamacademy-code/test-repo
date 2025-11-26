from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    APP_NAME: str = "SUPERCLAIMS API"
    API_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    GOOGLE_API_KEY: str
    LLM_MODEL: str = "gemini-2.5-flash"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_RETRIES: int = 3
    
    ALLOWED_ORIGINS: List[str] = ["*"]
    LOG_LEVEL: str = "INFO"
    
    UPLOAD_DIR: str = "uploaded_documents"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_FILE_TYPES: List[str] = [".pdf"]

settings = Settings()

