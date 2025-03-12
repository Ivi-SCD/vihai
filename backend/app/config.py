import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    API_URL: str
    GROQ_API_KEY: str
    MODEL_NAME: str = "deepseek-r1-distill-llama-70b"
    MODEL_CHAT_NAME: str =  "llama3-8b-8192"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    """Cached settings to avoid reloading from env file"""
    return Settings()