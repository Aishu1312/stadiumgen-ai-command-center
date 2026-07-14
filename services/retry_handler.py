import re
import streamlit as st
from google.genai import errors as genai_errors
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
from tenacity.wait import wait_base
from utils.logging_utils import get_logger
from config.ai_config import ai_settings

logger = get_logger(__name__)



def ui_retry_callback(retry_state):
    """Provides user-friendly feedback during retries."""
    exc = retry_state.outcome.exception()
    msg = "Connecting to AI..."
    if isinstance(exc, genai_errors.ClientError):
        code = getattr(exc, 'code', None)
        if code == 429:
            msg = "Waiting before retry..."
        else:
            msg = "Preparing personalized insights..."
    elif isinstance(exc, genai_errors.APIError):
        msg = "Analyzing your request..."
    
    logger.warning(f"AI Retry Attempt {retry_state.attempt_number}: {msg} - Reason: {str(exc)}")
    
    try:
        st.toast(f"⏳ {msg}")
    except Exception:
        pass

def get_retry_decorator():
    """
    Returns a configured tenacity retry decorator for AI calls.
    """
    return retry(
        stop=stop_after_attempt(ai_settings.max_retries),
        wait=wait_exponential(
            multiplier=ai_settings.initial_retry_delay, 
            min=ai_settings.initial_retry_delay, 
            max=ai_settings.max_retry_delay
        ),
        retry=retry_if_exception_type((genai_errors.APIError, genai_errors.ClientError)),
        before_sleep=ui_retry_callback
    )
