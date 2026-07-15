import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

def validate_api_key(api_key: Optional[str]) -> bool:
    """Validates that the API key is present and looks reasonable."""
    if not api_key or not str(api_key).strip() or str(api_key).strip() in ("your_gemini_api_key_here", "your_groq_api_key_here"):
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
    """Validates that the prompt is not empty."""
    if not prompt or not str(prompt).strip():
        logger.error("AI Validation Error: Prompt is empty.")
        return False
    return True
