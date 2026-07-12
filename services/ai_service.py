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

def ui_retry_callback(retry_state):
    """Provides user-friendly feedback during exponential backoff retries."""
    exc = retry_state.outcome.exception()
    msg = "Connecting to AI... Retrying..."
    if isinstance(exc, google_exceptions.ResourceExhausted):
        if "quota" in str(exc).lower():
            msg = "The AI usage limit has been reached. Please try again later."
        else:
            msg = "Too many requests. Waiting before retrying."
    elif isinstance(exc, google_exceptions.DeadlineExceeded):
        msg = "The request took longer than expected. Retrying automatically..."
    
    logger.warning(f"AI Retry: {msg}")
    try:
        st.toast(f"⏳ {msg}")
    except Exception:
        pass

class GeminiClient:
    """Centralized client for Google Gemini API."""
    def __init__(self):
        self.model_name = settings.DEFAULT_MODEL
        self.generation_config = genai.types.GenerationConfig(
            temperature=settings.TEMPERATURE,
            max_output_tokens=settings.MAX_OUTPUT_TOKENS
        )
        self.is_configured = False
        self.config_error = None
        self.configure()

    def configure(self) -> None:
        """Initializes the Gemini model safely. Prioritizes ENV vars over secrets.toml for test compatibility."""
        api_key = None
        
        # 1. Check secrets.toml first
        try:
            if "GEMINI_API_KEY" in st.secrets:
                api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass
            
        # 2. Let OS Environment Variables OVERRIDE secrets.toml (critical for CI/CD test injections)
        env_key = os.environ.get("GEMINI_API_KEY")
        if env_key and env_key.strip() and env_key != "your_gemini_api_key_here":
            api_key = env_key

        # 3. Fallback check
        if not api_key or api_key.strip() == "" or api_key == "your_gemini_api_key_here":
            self.config_error = "Missing configuration"
            self.is_configured = False
            return

        try:
            genai.configure(api_key=api_key)
            self.is_configured = True
            self.config_error = None
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            self.config_error = "SDK configuration failed"
            self.is_configured = False

    def get_model(self, fallback: bool = False) -> Optional[Any]:
        if not self.is_configured:
            return None
        model_to_use = "gemini-1.5-flash-8b" if fallback else self.model_name
        try:
            # Removed safety_settings=None as it may crash older SDKs
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

def map_google_error(exc: Exception) -> str:
    """Maps raw Google exceptions to exact user-friendly required strings."""
    if isinstance(exc, google_exceptions.NotFound):
        return "Model unavailable"
    elif isinstance(exc, google_exceptions.PermissionDenied):
        return "Authentication failed"
    elif isinstance(exc, google_exceptions.ResourceExhausted):
        if "quota" in str(exc).lower():
            return "Quota exceeded"
        return "Temporary service issue"
    elif isinstance(exc, google_exceptions.DeadlineExceeded):
        return "Network timeout"
    elif isinstance(exc, google_exceptions.ServiceUnavailable):
        return "Temporary service issue"
    elif isinstance(exc, google_exceptions.InvalidArgument):
        if "API key" in str(exc) or "key" in str(exc).lower():
            return "Authentication failed"
        return "Temporary service issue"
    elif isinstance(exc, ValueError):
        return "Temporary service issue"
    elif "timeout" in str(exc).lower():
        return "Network timeout"
    
    logger.error(f"Unhandled AI exception: {str(exc)}", exc_info=True)
    return "Temporary service issue"

@retry(
    stop=stop_after_attempt(settings.AI_RETRY_COUNT), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((google_exceptions.ResourceExhausted, google_exceptions.ServiceUnavailable, google_exceptions.DeadlineExceeded)),
    before_sleep=ui_retry_callback
)
def _generate_response_inner(prompt: str, system_instruction: str = "", context: str = "") -> str:
    if not client.is_configured:
        return "Missing configuration"

    model = client.get_model()
    if not model:
        return "Model unavailable"
    
    full_prompt = f"System: {system_instruction}\n{context}\nUser: {prompt}" if system_instruction else f"{context}{prompt}"
    
    try:
        response = model.generate_content(
            full_prompt, 
            request_options={"timeout": settings.AI_TIMEOUT}
        )
        if not response.text:
            return "Empty response"
        return response.text
    except google_exceptions.NotFound as e:
        logger.error(f"Model {client.model_name} not found. Fallback: {e}")
        fallback_model = client.get_model(fallback=True)
        if fallback_model:
            try:
                response = fallback_model.generate_content(
                    full_prompt, 
                    request_options={"timeout": settings.AI_TIMEOUT}
                )
                if not response.text:
                    return "Empty response"
                return response.text
            except Exception as inner_e:
                logger.error(f"Fallback model failed: {inner_e}")
                return "Model unavailable"
        return "Model unavailable"
    except (google_exceptions.ResourceExhausted, google_exceptions.ServiceUnavailable, google_exceptions.DeadlineExceeded) as e:
        raise e  # Allow tenacity to handle the retry
    except Exception as e:
        return map_google_error(e)

def generate_response(prompt: str, system_instruction: str = "") -> str:
    """Wrapper to handle RetryError gracefully."""
    if not prompt or not str(prompt).strip():
        return "Empty response"

    context = ""
    if "current_page_context" in st.session_state:
        context = f"Current Context: {st.session_state.current_page_context}\n\n"

    try:
        return _generate_response_inner(prompt, system_instruction, context)
    except RetryError as e:
        last_exc = e.last_attempt.exception() if e.last_attempt else None
        return map_google_error(last_exc)
    except Exception as e:
        return map_google_error(e)

@retry(
    stop=stop_after_attempt(settings.AI_RETRY_COUNT), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((google_exceptions.ResourceExhausted, google_exceptions.ServiceUnavailable, google_exceptions.DeadlineExceeded)),
    before_sleep=ui_retry_callback
)
def _generate_response_stream_inner(prompt: str, system_instruction: str = "", context: str = "") -> Generator[str, None, None]:
    if not client.is_configured:
        yield "Missing configuration"
        return

    model = client.get_model()
    if not model:
        yield "Model unavailable"
        return
        
    full_prompt = f"System: {system_instruction}\n{context}\nUser: {prompt}" if system_instruction else f"{context}{prompt}"
    
    try:
        response = model.generate_content(
            full_prompt, 
            stream=True, 
            request_options={"timeout": settings.AI_TIMEOUT}
        )
        has_yielded = False
        for chunk in response:
            try:
                if chunk.text:
                    has_yielded = True
                    yield chunk.text
            except ValueError:
                pass
        
        if not has_yielded:
            yield "Empty response"
            
    except google_exceptions.NotFound as e:
        logger.error(f"Model {client.model_name} not found in stream. Fallback: {e}")
        fallback_model = client.get_model(fallback=True)
        if fallback_model:
            try:
                response = fallback_model.generate_content(
                    full_prompt, 
                    stream=True, 
                    request_options={"timeout": settings.AI_TIMEOUT}
                )
                has_yielded = False
                for chunk in response:
                    try:
                        if chunk.text:
                            has_yielded = True
                            yield chunk.text
                    except ValueError:
                        pass
                if not has_yielded:
                    yield "Empty response"
            except Exception as inner_e:
                logger.error(f"Fallback model stream failed: {inner_e}")
                yield "Model unavailable"
        else:
            yield "Model unavailable"
    except (google_exceptions.ResourceExhausted, google_exceptions.ServiceUnavailable, google_exceptions.DeadlineExceeded) as e:
        raise e  # Allow tenacity to retry
    except Exception as e:
        yield map_google_error(e)

def generate_response_stream(prompt: str, system_instruction: str = "") -> Generator[str, None, None]:
    """Generates a streaming response for interactive chat UIs."""
    if not prompt or not str(prompt).strip():
        yield "Empty response"
        return

    context = ""
    if "current_page_context" in st.session_state:
        context = f"Current Context: {st.session_state.current_page_context}\n\n"

    try:
        yield from _generate_response_stream_inner(prompt, system_instruction, context)
    except RetryError as e:
        last_exc = e.last_attempt.exception() if e.last_attempt else None
        yield map_google_error(last_exc)
    except Exception as e:
        yield map_google_error(e)

def translate_text(text: str, target_language: str) -> str:
    """Translates text using Gemini."""
    prompt = f"Translate the following text to {target_language}. Return ONLY the translation, no extra text.\n\n{text}"
    return generate_response(prompt)

def generate_emergency_sop(incident_type: str, location: str) -> str:
    """Generates an Emergency Standard Operating Procedure."""
    prompt = f"Generate a concise, 5-step Emergency Standard Operating Procedure (SOP) for a {incident_type} incident at {location} in a busy stadium."
    return generate_response(prompt, system_instruction=Prompts.SYSTEM_EMERGENCY_SOP)
