from dataclasses import dataclass, field
from typing import List

@dataclass
class AIConfig:
    # Model settings
    primary_model: str = "gemini-2.0-flash"
    backup_models: List[str] = field(default_factory=lambda: ["gemini-2.5-flash", "gemini-2.5-pro"])
    temperature: float = 0.7
    max_output_tokens: int = 8192
    
    # Retry & Timeout settings
    ai_timeout_seconds: int = 120
    max_retries: int = 5  # Increased for better resilience
    initial_retry_delay: float = 2.0
    max_retry_delay: float = 15.0
    
    # Caching
    cache_ttl_seconds: int = 3600  # 1 hour cache for expensive operations

ai_settings = AIConfig()
