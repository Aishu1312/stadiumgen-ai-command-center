import os
import streamlit as st
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

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
        """Securely retrieves the Gemini API Key from Streamlit secrets or environment (case-insensitive)."""
        possible_keys = ["GEMINI_API_KEY", "GOOGLE_API_KEY", "API_KEY"]
        
        # Check st.secrets (case-insensitive)
        try:
            if hasattr(st, "secrets") and st.secrets:
                # Convert all keys in st.secrets to uppercase for case-insensitive matching
                secrets_dict = {str(k).upper(): v for k, v in dict(st.secrets).items()}
                for key_name in possible_keys:
                    if key_name in secrets_dict:
                        val = str(secrets_dict[key_name]).strip()
                        if val and val != "your_gemini_api_key_here":
                            return val
        except Exception as e:
            pass
            
        # Check os.environ (case-insensitive)
        env_dict = {str(k).upper(): v for k, v in os.environ.items()}
        for key_name in possible_keys:
            if key_name in env_dict:
                val = str(env_dict[key_name]).strip()
                if val and val != "your_gemini_api_key_here":
                    return val
                    
        return None

settings = Settings()
