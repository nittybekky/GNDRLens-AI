from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SafeSpace AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    GOOGLE_API_KEY: str = "your-secret-key-here"  
    
    class Config:
        env_file = ".env"

settings = Settings() 