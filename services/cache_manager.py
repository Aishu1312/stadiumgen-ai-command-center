import streamlit as st
from config.ai_config import ai_settings
from typing import Callable
from functools import wraps

def ai_cache(func: Callable) -> Callable:
    """
    Decorator for caching AI responses.
    Uses st.cache_data with a configured TTL.
    Handles unhashable parameters intelligently by omitting them from cache keys if needed, 
    but for now defaults to standard Streamlit caching behavior with show_spinner=False.
    """
    return st.cache_data(ttl=ai_settings.cache_ttl_seconds, show_spinner=False)(func)

def model_cache(func: Callable) -> Callable:
    """
    Decorator for caching the AI model instance/client.
    Uses st.cache_resource which is ideal for database connections and API clients.
    """
    return st.cache_resource(show_spinner=False)(func)
