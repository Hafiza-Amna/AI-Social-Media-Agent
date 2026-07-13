import os
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.
    """
    APP_NAME: str = os.getenv("APP_NAME", "AI Social Media Agent")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "groq/llama-3.3-70b-versatile")
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

    class Config:
        env_file = ".env"

# Create a global settings object to be imported across the application
settings = Settings()
