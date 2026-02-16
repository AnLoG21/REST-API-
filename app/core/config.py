from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = 'postgresql://postgres:postgres@localhost:5432/organizations_db'
    API_KEY: str = 'test-api-key-12345'
    LOG_LEVEL: str = 'INFO'
    PROJECT_NAME: str = 'Organizations Directory API'
    VERSION: str = '1.0.0'
    
    class Config:
        env_file = '.env'
        case_sensitive = True


settings = Settings()

