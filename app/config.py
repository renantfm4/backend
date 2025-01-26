from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/mydatabase"
    
    # JWT Configuration
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Project Settings
    PROJECT_NAME: str = "FastAPI Advanced Project"
    DEBUG: bool = False

    # Load .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8" ,extra='allow') 

settings = Settings()