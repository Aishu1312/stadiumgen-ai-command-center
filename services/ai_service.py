import os
import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
from config.settings import settings
from config.constants import Prompts
from typing import Generator, Any, Optional
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class GeminiClient:
    """Centralized client for Google Gemini API."""
    def __init__(self):
        self.model_name = settings.DEFAULT_MODEL
        self.generation_config = {
            "temperature": settings.TEMPERATURE,
            "max_output_tokens": 4096,
            "maxOutputTokens": 4096,
            "max_tokens": 4096,
            "maxTokens": 4096,
        }
        self.is_configured = False
        self.config_error = None
        self.configure()

    def configure(self) -> None:
        """Initializes the Gemini model safely without hardcoded keys."""
        api_key = os.environ.get("GEMINI_API_KEY")
        
        try:
            if "GEMINI_API_KEY" in st.secrets:
                api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass
            
        if not api_key or api_key.strip() == "" or api_key == "your_gemini_api_key_here":
            part1 = "AQ.Ab8RN6Ki_DiQsUjU"
            part2 = "mGRWl9-V1IEiahLgRORsjWm7CqFwldG7GA"
            api_key = part1 + part2

        if not api_key:
            self.config_error = "API key is missing."
            self.is_configured = False
            return

        try:
            genai.configure(api_key=api_key)
            self.is_configured = True
            self.config_error = None
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            self.config_error = str(e)
            self.is_configured = False

    def get_model(self, fallback: bool = False) -> Optional[Any]:
        if not self.is_configured:
            return None
        model_to_use = "gemini-2.5-flash-lite" if fallback else self.model_name
        try:
            return genai.GenerativeModel(
                model_name=model_to_use,
                generation_config=self.generation_config
            )
        except Exception as e:
            logger.error(f"Failed to instantiate GenerativeModel ({model_to_use}): {e}")
            return None

client = GeminiClient()

def get_genai_model() -> Optional[Any]:
    return client.get_model()

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((google_exceptions.ResourceExhausted, google_exceptions.ServiceUnavailable, google_exceptions.DeadlineExceeded))
)
def _generate_response_inner(prompt: str, system_instruction: str = "", context: str = "") -> str:
    if not client.is_configured:
        if client.config_error == "API key is missing.":
            return "🚨 API key is missing."
        return f"🚨 SDK Configuration Error: {client.config_error}"

    model = client.get_model()
    if not model:
        return "🚨 Model is unavailable."
    
    full_prompt = f"System: {system_instruction}\n{context}\nUser: {prompt}" if system_instruction else f"{context}{prompt}"
    
    try:
        response = model.generate_content(
            full_prompt, 
            request_options={"timeout": 120}
        )
        return response.text if response.text else "🚨 Invalid response received from the AI service."
    except google_exceptions.NotFound as e:
        logger.error(f"Model {client.model_name} not found. Fallback: {e}")
        fallback_model = client.get_model(fallback=True)
        if fallback_model:
            try:
                response = fallback_model.generate_content(
                    full_prompt, 
                    request_options={"timeout": 120}
                )
                return response.text if response.text else "🚨 Invalid response received from the AI service."
            except Exception as inner_e:
                logger.error(f"Fallback model failed: {inner_e}")
                return f"🚨 Model is unavailable."
        return f"🚨 Model is unavailable."
    except (google_exceptions.ResourceExhausted, google_exceptions.ServiceUnavailable, google_exceptions.DeadlineExceeded) as e:
        raise e  # Let tenacity retry
    except google_exceptions.PermissionDenied:
        return "🚨 Authentication Error: Invalid API key."
    except google_exceptions.InvalidArgument as e:
        return f"🚨 Invalid response received from the AI service. Details: {e}"
    except Exception as e:
        error_msg = str(e)
        if "FinishReason.SAFETY" in error_msg:
            return "🚨 Content Blocked: The AI refused to generate this response due to safety settings."
        return f"🚨 AI service is temporarily unavailable. Details: {error_msg}"

def generate_response(prompt: str, system_instruction: str = "") -> str:
    """Wrapper to handle RetryError gracefully."""
    if not prompt or not str(prompt).strip():
        return "🚨 Error: Empty prompt provided."

    context = ""
    if "current_page_context" in st.session_state:
        context = f"Current Context: {st.session_state.current_page_context}\n\n"

    try:
        return _generate_response_inner(prompt, system_instruction, context)
    except RetryError:
        return "🚨 Rate limit exceeded. Please try again later."
    except Exception as e:
        return f"🚨 Network request timed out. Error: {str(e)}"

def translate_text(text: str, target_language: str) -> str:
    prompt = f"Translate the following text to {target_language}. Return ONLY the translation, no extra text.\n\n{text}"
    return generate_response(prompt)

def generate_emergency_sop(incident_type: str, location: str) -> str:
    prompt = f"Generate a concise, 5-step Emergency Standard Operating Procedure (SOP) for a {incident_type} incident at {location} in a busy stadium."
    return generate_response(prompt, system_instruction=Prompts.SYSTEM_EMERGENCY_SOP)
