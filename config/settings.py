from typing import Dict, Any

class Settings:
    # Security
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_LOGIN_ATTEMPTS: int = 3
    
    # UI Configuration
    THEME_COLOR: str = "#4CAF50"
    COMPANY_NAME: str = "StadiumGen AI"
    
    # AI Configuration
    DEFAULT_MODEL: str = "gemini-1.5-flash"
    TEMPERATURE: float = 0.7
    MAX_OUTPUT_TOKENS: int = 8192  # Increased to 8192 to prevent report truncation
    AI_TIMEOUT: int = 120  # Restored to 120s to allow complex report generation
    AI_RETRY_COUNT: int = 3
    AI_SAFETY_SETTINGS: Any = None
    
    # Cache Configuration
    CACHE_TTL: int = 300  # 5 minutes

settings = Settings()
