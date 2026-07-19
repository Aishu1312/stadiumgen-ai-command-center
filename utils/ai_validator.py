import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

def validate_api_key(api_key: Optional[str]) -> bool:
    """Validates that the API key is present and looks reasonable."""
    if not api_key or not str(api_key).strip() or str(api_key).strip() in ("your_groq_api_key_here", "your_groq_api_key"):
        logger.error("AI Validation Error: API key is missing or invalid.")
        return False
    return True

def validate_model(model_name: str, supported_models: List[str]) -> bool:
    """Validates that the requested model is in the list of supported models."""
    if model_name not in supported_models:
        logger.error(f"AI Validation Error: Model '{model_name}' is not supported.")
        return False
    return True

def validate_request_parameters(prompt: str) -> bool:
    """Validates that the prompt is not empty and protects against basic prompt injection."""
    if not prompt or not str(prompt).strip():
        logger.error("AI Validation Error: Prompt is empty.")
        return False
        
    prompt_lower = str(prompt).lower()
    
    # Basic prompt injection keywords protection
    dangerous_patterns = [
        "ignore all previous instructions",
        "you are now",
        "system prompt",
        "bypass",
        "jailbreak",
        "as an ai",
        "developer mode"
    ]
    
    for pattern in dangerous_patterns:
        if pattern in prompt_lower:
            logger.warning(f"AI Validation Security Warning: Potential prompt injection detected. Pattern: '{pattern}'")
            return False
            
    # Length validation to prevent DOS
    if len(prompt) > 2000:
        logger.warning("AI Validation Error: Prompt exceeds maximum allowed length.")
        return False
        
    return True
