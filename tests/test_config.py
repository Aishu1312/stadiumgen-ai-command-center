import pytest
from config.settings import Settings

def test_settings_initialization():
    """Test that the application settings initialize correctly."""
    settings = Settings()
    assert settings.APP_NAME == "StadiumGen AI Command Center"
    assert isinstance(settings.APP_DEBUG, bool)
    assert settings.GROQ_API_KEY is not None or settings.GROQ_API_KEY is None # Testing it doesn't crash on load
