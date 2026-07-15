import os
import streamlit as st
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

def get_streamlit_secret(key_name: str) -> Optional[str]:
    try:
        if hasattr(st, "secrets") and st.secrets:
            secrets_dict = {str(k).upper(): v for k, v in dict(st.secrets).items()}
            return str(secrets_dict.get(key_name.upper(), "")).strip() or None
    except Exception:
        pass
    return None

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application
    APP_NAME: str = "StadiumGen AI Command Center"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8501
    APP_VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: str = Field(default="your_secret_key_here")
    JWT_SECRET_KEY: str = Field(default="your_jwt_secret_here")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_LOGIN_ATTEMPTS: int = 3

    # UI Configuration
    THEME_COLOR: str = "#4CAF50"
    COMPANY_NAME: str = "StadiumGen AI"
    DEFAULT_LANGUAGE: str = "English"

    # Groq AI
    GROQ_API_KEY: Optional[str] = None

    # Database
    DATABASE_URL: str = "sqlite:///stadiumgen.db"

    # Streamlit
    STREAMLIT_SERVER_PORT: int = 8501
    STREAMLIT_SERVER_HEADLESS: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"

    # Cache Configuration
    CACHE_TTL: int = 3600

    @property
    def api_key_resolved(self) -> Optional[str]:
        """Securely retrieves the Groq API Key with fallback logic."""
        possible_keys = ["GROQ_API_KEY", "API_KEY"]
        
        # 1. Streamlit secrets
        for key in possible_keys:
            val = get_streamlit_secret(key)
            if val and val not in ["your_groq_api_key_here", "your_groq_api_key"]:
                return val
        
        # 2. Pydantic settings (.env or exact os.environ match)
        if self.GROQ_API_KEY and self.GROQ_API_KEY not in ["your_groq_api_key_here", "your_groq_api_key"]:
            return self.GROQ_API_KEY
        
        # 3. Raw os.environ fallback
        env_dict = {str(k).upper(): v for k, v in os.environ.items()}
        for key in possible_keys:
            val = env_dict.get(key)
            if val and val not in ["your_groq_api_key_here", "your_groq_api_key"]:
                return val

        return None

settings = Settings()
