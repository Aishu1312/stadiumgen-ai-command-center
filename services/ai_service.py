import os
import streamlit as st
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
from config.settings import settings
from config.constants import Prompts
from typing import Generator, Any, Optional
import logging
from services.exceptions import AIError

load_dotenv()
logger = logging.getLogger(__name__)

def ui_retry_callback(retry_state):
    """Provides user-friendly feedback during exponential backoff retries."""
    exc = retry_state.outcome.exception()
    msg = "Connecting to AI... Retrying..."
    if isinstance(exc, genai_errors.ClientError):
        code = getattr(exc, 'code', None)
        if code == 429:
            msg = "The AI usage limit has been reached. Please try again later."
        else:
            msg = "Too many requests. Waiting before retrying."
    elif isinstance(exc, genai_errors.APIError):
        msg = "The request took longer than expected. Retrying automatically..."
    
    logger.warning(f"AI Retry: {msg}")
    try:
        st.toast(f"⏳ {msg}")
    except Exception:
        pass

class GeminiClient:
    """Centralized client for Google Gemini API using google-genai."""
    def __init__(self):
        self.model_name = settings.DEFAULT_MODEL
        self.is_configured = False
        self.config_error = None
        self.client = None

    def configure(self) -> None:
        """Initializes the Gemini model safely."""
        api_key = settings.GEMINI_API_KEY

        if not api_key:
            self.config_error = "Missing configuration"
            self.is_configured = False
            return

        try:
            self.client = genai.Client(
                api_key=api_key,
                http_options={'timeout': settings.AI_TIMEOUT * 1000} # Optional depending on SDK version, we'll configure per-request if needed
            )
            
            # Validate configured model without failing on network/quota errors
            try:
                supported_models = [m.name for m in self.client.models.list()]
                expected_model_name = self.model_name if self.model_name.startswith("models/") else f"models/{self.model_name}"
                
                if expected_model_name not in supported_models:
                    logger.error(f"Configured model {self.model_name} is unsupported. Available: {supported_models}")
                    self.config_error = "Model unavailable"
                    self.is_configured = False
                    return
            except Exception as e:
                logger.warning(f"Could not validate model list during startup, proceeding: {e}")

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

client = GeminiClient()

def map_google_error(exc: Exception) -> str:
    """Maps raw Google exceptions to exact user-friendly required strings."""
    if isinstance(exc, genai_errors.ClientError):
        code = getattr(exc, 'code', None)
        if code == 404:
            return "Unsupported model"
        elif code in (401, 403):
            return "Invalid API credentials"
        elif code == 429:
            return "Rate limit reached"
        elif code == 400:
            return "Configuration error"
        else:
            return "Service temporarily unavailable"
    elif isinstance(exc, genai_errors.APIError):
        return "Service temporarily unavailable"
    elif isinstance(exc, ValueError):
        return "Unexpected AI response"
    elif "timeout" in str(exc).lower():
        return "Timeout"
    
    logger.error(f"Unhandled AI exception: {str(exc)}", exc_info=True)
    return "Service temporarily unavailable"

@retry(
    stop=stop_after_attempt(settings.AI_RETRY_COUNT), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((genai_errors.APIError, genai_errors.ClientError)),
    before_sleep=ui_retry_callback
)
def _generate_response_inner(prompt: str, system_instruction: str = "", context: str = "") -> str:
    genai_client = client.get_client()
    
    if not genai_client:
        if client.config_error == "Missing configuration":
            return "Missing configuration"
        return "Model unavailable"
    
    config_kwargs = {
        "temperature": settings.TEMPERATURE,
        "max_output_tokens": settings.MAX_OUTPUT_TOKENS
    }
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction
        
    config = types.GenerateContentConfig(**config_kwargs)
    full_prompt = f"{context}{prompt}"
    
    try:
        response = genai_client.models.generate_content(
            model=client.model_name,
            contents=full_prompt, 
            config=config
        )
        if not response.text:
            return "Empty response"
        return response.text
    except genai_errors.ClientError as e:
        code = getattr(e, 'code', None)
        if code == 404:
            logger.error(f"Model {client.model_name} not found: {e}")
            return "Model unavailable"
        elif code == 429 or (code and code >= 500):
            logger.warning(f"ClientError: {e}")
            raise e  # Allow tenacity to handle the retry
        else:
            return map_google_error(e)
    except genai_errors.APIError as e:
        raise e  # Allow tenacity to handle the retry
    except Exception as e:
        return map_google_error(e)

def generate_response(prompt: str, system_instruction: str = "") -> str:
    """Wrapper to handle RetryError gracefully."""
    if not prompt or not str(prompt).strip():
        raise AIError("Empty response")

    context = ""
    if "current_page_context" in st.session_state:
        context = f"Current Context: {st.session_state.current_page_context}\n\n"

    try:
        response = _generate_response_inner(prompt, system_instruction, context)
        if response in ["Missing configuration", "Model unavailable", "Empty response"]:
            if response == "Missing configuration":
                raise AIError("Missing API credentials")
            elif response == "Model unavailable":
                raise AIError("Unsupported model")
            else:
                raise AIError("Unexpected AI response")
        return response
    except RetryError as e:
        last_exc = e.last_attempt.exception() if e.last_attempt else None
        raise AIError(map_google_error(last_exc))
    except AIError:
        raise
    except Exception as e:
        raise AIError(map_google_error(e))

@retry(
    stop=stop_after_attempt(settings.AI_RETRY_COUNT), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((genai_errors.APIError, genai_errors.ClientError)),
    before_sleep=ui_retry_callback
)
def _generate_response_stream_inner(prompt: str, system_instruction: str = "", context: str = "") -> Generator[str, None, None]:
    genai_client = client.get_client()
    
    if not genai_client:
        if client.config_error == "Missing configuration":
            yield "Missing configuration"
        else:
            yield "Model unavailable"
        return
        
    config_kwargs = {
        "temperature": settings.TEMPERATURE,
        "max_output_tokens": settings.MAX_OUTPUT_TOKENS
    }
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction
        
    config = types.GenerateContentConfig(**config_kwargs)
    full_prompt = f"{context}{prompt}"
    
    try:
        response = genai_client.models.generate_content_stream(
            model=client.model_name,
            contents=full_prompt, 
            config=config
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
            
    except genai_errors.ClientError as e:
        code = getattr(e, 'code', None)
        if code == 404:
            logger.error(f"Model {client.model_name} not found in stream: {e}")
            yield "Model unavailable"
        elif code == 429 or (code and code >= 500):
            raise e  # Allow tenacity to retry
        else:
            yield map_google_error(e)
    except genai_errors.APIError as e:
        raise e  # Allow tenacity to retry
    except Exception as e:
        yield map_google_error(e)

def generate_response_stream(prompt: str, system_instruction: str = "") -> Generator[str, None, None]:
    """Generates a streaming response for interactive chat UIs."""
    if not prompt or not str(prompt).strip():
        raise AIError("Empty response")

    context = ""
    if "current_page_context" in st.session_state:
        context = f"Current Context: {st.session_state.current_page_context}\n\n"

    try:
        stream = _generate_response_stream_inner(prompt, system_instruction, context)
        first_chunk = next(stream)
        if first_chunk in ["Missing configuration", "Model unavailable", "Empty response"]:
            if first_chunk == "Missing configuration":
                raise AIError("Missing API credentials")
            elif first_chunk == "Model unavailable":
                raise AIError("Unsupported model")
            else:
                raise AIError("Unexpected AI response")
        
        yield first_chunk
        yield from stream
    except StopIteration:
        pass
    except RetryError as e:
        last_exc = e.last_attempt.exception() if e.last_attempt else None
        raise AIError(map_google_error(last_exc))
    except AIError:
        raise
    except Exception as e:
        raise AIError(map_google_error(e))

def translate_text(text: str, target_language: str) -> str:
    """Translates text using Gemini."""
    prompt = f"Translate the following text to {target_language}. Return ONLY the translation, no extra text.\n\n{text}"
    return generate_response(prompt)

def generate_emergency_sop(incident_type: str, location: str) -> str:
    """Generates an Emergency Standard Operating Procedure."""
    prompt = f"Generate a concise, 5-step Emergency Standard Operating Procedure (SOP) for a {incident_type} incident at {location} in a busy stadium."
    return generate_response(prompt, system_instruction=Prompts.SYSTEM_EMERGENCY_SOP)
