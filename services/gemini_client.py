import logging
from typing import Optional, Any
from google import genai
from config.settings import settings
from config.ai_config import ai_settings
from services.model_router import ModelRouter
from utils.ai_validator import validate_api_key

logger = logging.getLogger(__name__)

class GeminiClient:
    """Centralized client for Google Gemini API."""
    def __init__(self):
        self.router = ModelRouter()
        self.is_configured = False
        self.config_error = None
        self.client = None

    def configure(self) -> None:
        """Initializes the Gemini model safely."""
        api_key = settings.api_key_resolved

        if not validate_api_key(api_key):
            self.config_error = "Missing configuration"
            self.is_configured = False
            return

        try:
            self.client = genai.Client(
                api_key=api_key,
                http_options={'timeout': ai_settings.ai_timeout_seconds * 1000}
            )
            
            # Fetch supported models quickly
            try:
                supported_models = [m.name for m in self.client.models.list()]
                # Router handles finding the best model
                selected_model = self.router.get_next_available_model(supported_models)
                if not selected_model:
                    self.config_error = "Model unavailable"
                    self.is_configured = False
                    return
            except Exception as e:
                logger.warning(f"Could not validate model list during startup: {e}")

            self.is_configured = True
            self.config_error = None
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            self.config_error = "SDK configuration failed"
            self.is_configured = False

    def get_client(self) -> Optional[Any]:
        if not self.is_configured:
            self.configure()
        return self.client if self.is_configured else None
