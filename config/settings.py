"""
Centralized Configuration for WorldCup AI Command Center.
"""

from typing import Dict, Any

class Settings:
    APP_NAME: str = "WorldCup AI Command Center"
    APP_VERSION: str = "2.0.0"
    DEFAULT_LANGUAGE: str = "English"
    
    # AI Settings
    DEFAULT_MODEL: str = "gemini-2.5-flash"
    MAX_OUTPUT_TOKENS: int = 4096
    TEMPERATURE: float = 0.7
    AI_TIMEOUT: int = 120
    AI_RETRY_COUNT: int = 3
    AI_SAFETY_SETTINGS: Any = None
    
    # UI Theme Settings
    THEME_COLORS: Dict[str, str] = {
        "primary": "#3b82f6",
        "secondary": "#8b5cf6",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "background": "#0f172a",
        "surface": "rgba(255, 255, 255, 0.05)",
        "text": "#f8fafc",
        "text_muted": "#94a3b8"
    }

settings = Settings()
