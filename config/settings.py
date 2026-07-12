import os
import streamlit as st
from typing import Dict, Any

class Settings:
    # Security
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_LOGIN_ATTEMPTS: int = 3
    
    # UI Configuration
    THEME_COLOR: str = "#4CAF50"
    COMPANY_NAME: str = "StadiumGen AI"
    APP_NAME: str = "StadiumGen AI"
    APP_VERSION: str = "1.0.0"
    DEFAULT_LANGUAGE: str = "English"
    
    # AI Configuration
    DEFAULT_MODEL: str = "gemini-2.5-flash"
    TEMPERATURE: float = 0.7
    MAX_OUTPUT_TOKENS: int = 8192  # Increased to 8192 to prevent report truncation
    AI_TIMEOUT: int = 120  # Restored to 120s to allow complex report generation
    AI_RETRY_COUNT: int = 3
    AI_SAFETY_SETTINGS: Any = None
    
    # Cache Configuration
    CACHE_TTL: int = 300  # 5 minutes

    @property
    def GEMINI_API_KEY(self) -> str | None:
        """Securely retrieves the Gemini API Key from Streamlit secrets or environment."""
        api_key = None
        try:
            if "GEMINI_API_KEY" in st.secrets:
                api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass

        if not api_key:
            env_key = os.environ.get("GEMINI_API_KEY")
            if env_key and env_key.strip() and env_key != "your_gemini_api_key_here":
                api_key = env_key

        if api_key and api_key.strip() and api_key != "your_gemini_api_key_here":
            return api_key
        return None

settings = Settings()
