from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    APP_NAME: str = "Insurance Claim Processing API"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # LLM settings
    GOOGLE_API_KEY: str
    LLM_MODEL: str = "gemini-2.5-flash"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_RETRIES: int = 3

    #PASSWORD
    API_PASSWORD: str
    
    # File upload settings
    UPLOAD_DIR: str = "uploaded_documents"

settings = Settings()

