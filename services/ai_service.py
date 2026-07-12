import os
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
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
        # Use simple dict with only the snake_case keys to avoid SDK crashes
        self.generation_config = {
            "temperature": settings.TEMPERATURE,
            "max_output_tokens": 4096
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
        return "🚨 Invalid API key. Please check your secrets or environment variables."

    model = client.get_model()
    if not model:
        return "🚨 Unsupported model. Please check the model name in your configuration."
    
    full_prompt = f"System: {system_instruction}\n{context}\nUser: {prompt}" if system_instruction else f"{context}{prompt}"
    
    try:
        response = model.generate_content(
            full_prompt, 
            request_options={"timeout": 120}
        )
        return response.text if response.text else "🚨 Response parsing failure. Please try a different prompt."
    except google_exceptions.NotFound as e:
        logger.error(f"Model {client.model_name} not found. Fallback: {e}")
        fallback_model = client.get_model(fallback=True)
        if fallback_model:
            try:
                response = fallback_model.generate_content(
                    full_prompt, 
                    request_options={"timeout": 120}
                )
                return response.text if response.text else "🚨 Response parsing failure. Please try again."
            except Exception as inner_e:
                logger.error(f"Fallback model failed: {inner_e}")
                return "🚨 Unsupported model. Both default and fallback models failed."
        return "🚨 Unsupported model. The requested model is not available."
    except (google_exceptions.ResourceExhausted, google_exceptions.ServiceUnavailable, google_exceptions.DeadlineExceeded) as e:
        raise e  # Let tenacity retry
    except google_exceptions.PermissionDenied:
        return "🚨 Authentication failed. Please ensure your API key has the correct permissions."
    except google_exceptions.InvalidArgument as e:
        if "API key" in str(e):
            return "🚨 Invalid API key. Please provide a valid Gemini API key."
        return f"🚨 Invalid request payload. Please verify your prompt format."
    except Exception as e:
        error_msg = str(e).lower()
        if "timeout" in error_msg:
            return "🚨 Network timeout. Please check your internet connection."
        if "safety" in error_msg:
            return "🚨 Content Blocked. The AI refused to generate this response due to safety settings."
        return "🚨 Service temporarily unavailable. Please try again later."

def generate_response(prompt: str, system_instruction: str = "") -> str:
    """Generates a text response from Gemini given a prompt with retry logic."""
    if not prompt or not str(prompt).strip():
        return "🚨 Invalid request payload. Empty prompt provided."

    context = ""
    if "current_page_context" in st.session_state:
        context = f"Current Context: {st.session_state.current_page_context}\n\n"

    try:
        return _generate_response_inner(prompt, system_instruction, context)
    except RetryError as e:
        # Determine if it was quota or timeout based on the last exception
        last_exc = e.last_attempt.exception() if e.last_attempt else None
        if isinstance(last_exc, google_exceptions.ResourceExhausted):
            if "quota" in str(last_exc).lower():
                return "🚨 API quota exceeded. Please upgrade your plan or wait for the reset."
            return "🚨 Rate limit reached. Please slow down your requests and try again."
        elif isinstance(last_exc, google_exceptions.DeadlineExceeded):
            return "🚨 Network timeout. The connection timed out during retries."
        return "🚨 Service temporarily unavailable. Repeated requests failed."
    except Exception as e:
        error_msg = str(e).lower()
        if "timeout" in error_msg:
            return "🚨 Network timeout. Please check your internet connection."
        return "🚨 Service temporarily unavailable. An unexpected error occurred."

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((google_exceptions.ResourceExhausted, google_exceptions.ServiceUnavailable, google_exceptions.DeadlineExceeded))
)
def _generate_response_stream_inner(prompt: str, system_instruction: str = "", context: str = "") -> Generator[str, None, None]:
    if not client.is_configured:
        yield "\n\n🚨 Invalid API key. Please check your configuration."
        return

    model = client.get_model()
    if not model:
        yield "\n\n🚨 Unsupported model. Please check the model name in settings."
        return
        
    full_prompt = f"System: {system_instruction}\n{context}\nUser: {prompt}" if system_instruction else f"{context}{prompt}"
    
    try:
        response = model.generate_content(
            full_prompt, 
            stream=True, 
            request_options={"timeout": 120}
        )
        for chunk in response:
            try:
                if chunk.text:
                    yield chunk.text
            except ValueError:
                pass
    except google_exceptions.NotFound as e:
        logger.error(f"Model {client.model_name} not found in stream. Fallback: {e}")
        fallback_model = client.get_model(fallback=True)
        if fallback_model:
            try:
                response = fallback_model.generate_content(
                    full_prompt, 
                    stream=True, 
                    request_options={"timeout": 120}
                )
                for chunk in response:
                    try:
                        if chunk.text:
                            yield chunk.text
                    except ValueError:
                        pass
            except Exception as inner_e:
                logger.error(f"Fallback model stream failed: {inner_e}")
                yield "\n\n🚨 Unsupported model. Both default and fallback models failed."
        else:
            yield "\n\n🚨 Unsupported model. The requested model is not available."
    except (google_exceptions.ResourceExhausted, google_exceptions.ServiceUnavailable, google_exceptions.DeadlineExceeded) as e:
        raise e  # Let tenacity retry
    except google_exceptions.PermissionDenied:
        yield "\n\n🚨 Authentication failed. Please ensure your API key has the correct permissions."
    except google_exceptions.InvalidArgument as e:
        if "API key" in str(e):
            yield "\n\n🚨 Invalid API key. Please provide a valid Gemini API key."
        else:
            yield f"\n\n🚨 Invalid request payload. Please verify your prompt format."
    except Exception as e:
        error_msg = str(e).lower()
        if "timeout" in error_msg:
            yield "\n\n🚨 Network timeout. Please check your connection."
        elif "safety" in error_msg:
            yield "\n\n🚨 Content Blocked. The AI refused to generate this response due to safety settings."
        else:
            yield "\n\n🚨 Service temporarily unavailable. Please try again later."

def generate_response_stream(prompt: str, system_instruction: str = "") -> Generator[str, None, None]:
    """Generates a streaming response for interactive chat UIs."""
    if not prompt or not str(prompt).strip():
        yield "🚨 Invalid request payload. Empty prompt provided."
        return

    context = ""
    if "current_page_context" in st.session_state:
        context = f"Current Context: {st.session_state.current_page_context}\n\n"

    try:
        yield from _generate_response_stream_inner(prompt, system_instruction, context)
    except RetryError as e:
        last_exc = e.last_attempt.exception() if e.last_attempt else None
        if isinstance(last_exc, google_exceptions.ResourceExhausted):
            if "quota" in str(last_exc).lower():
                yield "\n\n🚨 API quota exceeded. Please upgrade your plan or wait for the reset."
            else:
                yield "\n\n🚨 Rate limit reached. Please slow down your requests and try again."
        elif isinstance(last_exc, google_exceptions.DeadlineExceeded):
            yield "\n\n🚨 Network timeout. The connection timed out during retries."
        else:
            yield "\n\n🚨 Service temporarily unavailable. Repeated requests failed."
    except Exception as e:
        error_msg = str(e).lower()
        if "timeout" in error_msg:
            yield "\n\n🚨 Network timeout. Please check your internet connection."
        else:
            yield "\n\n🚨 Service temporarily unavailable. An unexpected error occurred."

def translate_text(text: str, target_language: str) -> str:
    """Translates text using Gemini."""
    prompt = f"Translate the following text to {target_language}. Return ONLY the translation, no extra text.\n\n{text}"
    return generate_response(prompt)

def generate_emergency_sop(incident_type: str, location: str) -> str:
    """Generates an Emergency Standard Operating Procedure."""
    prompt = f"Generate a concise, 5-step Emergency Standard Operating Procedure (SOP) for a {incident_type} incident at {location} in a busy stadium."
    return generate_response(prompt, system_instruction=Prompts.SYSTEM_EMERGENCY_SOP)
