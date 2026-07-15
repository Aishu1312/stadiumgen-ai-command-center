import streamlit as st
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from tenacity import RetryError
from typing import Generator, Any, Optional

from config.ai_config import ai_settings
from config.constants import Prompts
from services.exceptions import AIError
from services.gemini_client import GeminiClient
from services.retry_handler import get_retry_decorator
from services.cache_manager import ai_cache, model_cache
from utils.ai_validator import validate_request_parameters
from utils.logging_utils import get_logger
from utils.performance import track_time

logger = get_logger(__name__)

def map_google_error(exc: Exception) -> str:
    """Maps raw Google exceptions to exact user-friendly required strings."""
    if isinstance(exc, genai_errors.ClientError):
        code = getattr(exc, 'code', None)
        if code == 404:
            return "The AI model is temporarily unavailable. Please try again shortly."
        elif code in (401, 403):
            return "Invalid API credentials"
        elif code == 429:
            return "The AI assistant is temporarily experiencing high demand. Please try again in a few moments. All other features remain available."
        elif code == 400:
            return "Configuration error"
        else:
            return "The AI service is currently unavailable. Please try again later."
    elif isinstance(exc, genai_errors.APIError):
        return "The AI service is currently unavailable. Please try again later."
    elif isinstance(exc, ValueError):
        return "Unexpected AI response"
    elif "timeout" in str(exc.__class__.__name__).lower() or "timeout" in str(exc).lower():
        return "The AI service took too long to respond. Please try again later."
    
    logger.error(f"Unhandled AI exception: {str(exc)}", exc_info=True)
    return "The AI service is currently unavailable. Please try again later."



@model_cache
def get_ai_client() -> GeminiClient:
    """Singleton initialization for GeminiClient via Streamlit cache."""
    return GeminiClient()

@ai_cache
@get_retry_decorator()
@track_time
def _generate_response_inner(prompt: str, system_instruction: str = "", context: str = "") -> str:
    ai_service = get_ai_client()
    genai_client = ai_service.get_client()
    
    if not genai_client:
        if ai_service.config_error == "Missing configuration":
            return "Missing configuration"
        return "Model unavailable"
    
    config_kwargs = {
        "temperature": ai_settings.temperature,
        "max_output_tokens": ai_settings.max_output_tokens
    }
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction
        
    config = types.GenerateContentConfig(**config_kwargs)
    full_prompt = f"{context}{prompt}"
    current_model = ai_service.router.get_current_model()
    
    try:
        response = genai_client.models.generate_content(
            model=current_model,
            contents=full_prompt, 
            config=config
        )
        if not response.text:
            return "Empty response"
        return response.text
    except genai_errors.ClientError as e:
        code = getattr(e, 'code', None)
        if code in (404, 429):
            logger.warning(f"Model {current_model} failed with {code}, marking as failed to use fallback.")
            ai_service.router.mark_failed(current_model)
            ai_service.is_configured = False # Force re-config to select new model
            raise e # Tenacity will retry with the newly selected model
        elif code and code >= 500:
            raise e  # Allow tenacity to handle the retry on the same model
        else:
            return map_google_error(e)
    except genai_errors.APIError as e:
        raise e  # Allow tenacity to handle the retry
    except Exception as e:
        return map_google_error(e)

def generate_response(prompt: str, system_instruction: str = "") -> str:
    """Wrapper to handle RetryError gracefully."""
    if not validate_request_parameters(prompt):
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
                raise AIError("The AI model is temporarily unavailable. Please try again shortly.")
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

@get_retry_decorator()
@track_time
def _get_stream_and_first_chunk(prompt: str, system_instruction: str = "", context: str = ""):
    ai_service = get_ai_client()
    genai_client = ai_service.get_client()
    
    if not genai_client:
        if ai_service.config_error == "Missing configuration":
            return "Missing configuration", None
        else:
            return "Model unavailable", None
        
    config_kwargs = {
        "temperature": ai_settings.temperature,
        "max_output_tokens": ai_settings.max_output_tokens
    }
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction
        
    config = types.GenerateContentConfig(**config_kwargs)
    full_prompt = f"{context}{prompt}"
    current_model = ai_service.router.get_current_model()
    
    response = genai_client.models.generate_content_stream(
        model=current_model,
        contents=full_prompt, 
        config=config
    )
    
    stream = iter(response)
    try:
        first_chunk_obj = next(stream)
        first_chunk = first_chunk_obj.text if first_chunk_obj.text else ""
        while not first_chunk:
            first_chunk_obj = next(stream)
            first_chunk = first_chunk_obj.text if first_chunk_obj.text else ""
        return first_chunk, stream
    except StopIteration:
        return "Empty response", stream
    except genai_errors.ClientError as e:
        code = getattr(e, 'code', None)
        if code in (404, 429):
            logger.warning(f"Model {current_model} failed with {code}, marking as failed to use fallback.")
            ai_service.router.mark_failed(current_model)
            ai_service.is_configured = False
            raise e
        raise e

def generate_response_stream(prompt: str, system_instruction: str = "") -> Generator[str, None, None]:
    """Generates a streaming response for interactive chat UIs."""
    if not validate_request_parameters(prompt):
        raise AIError("Empty response")

    context = ""
    if "current_page_context" in st.session_state:
        context = f"Current Context: {st.session_state.current_page_context}\n\n"

    try:
        first_chunk, stream = _get_stream_and_first_chunk(prompt, system_instruction, context)
        
        if first_chunk in ["Missing configuration", "Model unavailable", "Empty response"]:
            if first_chunk == "Missing configuration":
                raise AIError("Missing API credentials")
            elif first_chunk == "Model unavailable":
                raise AIError("The AI model is temporarily unavailable. Please try again shortly.")
            else:
                raise AIError("Unexpected AI response")
        
        yield first_chunk
        
        if stream:
            for chunk in stream:
                try:
                    if chunk.text:
                        yield chunk.text
                except ValueError:
                    pass

    except StopIteration:
        pass
    except RetryError as e:
        last_exc = e.last_attempt.exception() if e.last_attempt else None
        raise AIError(map_google_error(last_exc))
    except AIError:
        raise
    except Exception as e:
        raise AIError(map_google_error(e))

@ai_cache
def translate_text(text: str, target_language: str) -> str:
    """Translates text using Gemini."""
    prompt = f"Translate the following text to {target_language}. Return ONLY the translation, no extra text.\n\n{text}"
    return generate_response(prompt)

@ai_cache
def generate_emergency_sop(incident_type: str, location: str) -> str:
    """Generates an Emergency Standard Operating Procedure."""
    prompt = f"Generate a concise, 5-step Emergency Standard Operating Procedure (SOP) for a {incident_type} incident at {location} in a busy stadium."
    return generate_response(prompt, system_instruction=Prompts.SYSTEM_EMERGENCY_SOP)
