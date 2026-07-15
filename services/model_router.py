from config.ai_config import ai_settings
from utils.logging_utils import get_logger
from typing import List, Optional

logger = get_logger(__name__)

class ModelRouter:
    """
    Manages the primary and fallback models. 
    If the primary model is unavailable or encounters permanent errors,
    it provides the next available backup model.
    """
    def __init__(self):
        self.primary = ai_settings.primary_model
        self.backups = ai_settings.backup_models
        self.current_model = self.primary
        self._failed_models = set()
        
    def mark_failed(self, model_name: str) -> None:
        """Marks a model as failed so we do not attempt to use it again in this session."""
        self._failed_models.add(model_name)
        logger.warning(f"Model {model_name} marked as failed.")
        
    def get_next_available_model(self, supported_models: List[str]) -> Optional[str]:
        """
        Returns the first model (primary or backup) that is supported and hasn't failed.
        """
        candidates = [self.primary] + self.backups
        
        for candidate in candidates:
            if candidate not in self._failed_models and candidate in supported_models:
                self.current_model = candidate
                return candidate
                
        logger.error("No available models found from primary or backups.")
        return None
        
    def get_current_model(self) -> str:
        return self.current_model
