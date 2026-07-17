import streamlit as st
import groq
from tenacity import RetryError
from typing import Generator, Any, Optional

from config.ai_config import ai_settings
from config.constants import Prompts
from services.exceptions import AIError
from services.groq_client import GroqClient
from services.retry_handler import get_retry_decorator
from services.cache_manager import ai_cache, model_cache
from utils.ai_validator import validate_request_parameters
from utils.logging_utils import get_logger
from utils.performance import track_time

logger = get_logger(__name__)

def map_groq_error(exc: Exception) -> str:
    """Maps raw Groq exceptions to exact user-friendly required strings."""
    if isinstance(exc, groq.APIStatusError):
        code = getattr(exc, 'status_code', None)
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
    elif isinstance(exc, groq.APIConnectionError):
        return "The AI service took too long to respond. Please try again later."
    elif isinstance(exc, groq.APIError):
        return "The AI service is currently unavailable. Please try again later."
    elif isinstance(exc, ValueError):
        return "Unexpected AI response"
    
    logger.error(f"Unhandled AI exception: {str(exc)}", exc_info=True)
    return "The AI service is currently unavailable. Please try again later."

@model_cache
def get_ai_client() -> GroqClient:
    """Singleton initialization for GroqClient via Streamlit cache."""
    return GroqClient()

@ai_cache
@get_retry_decorator()
@track_time
def _generate_response_inner(prompt: str, system_instruction: str = "", context: str = "") -> str:
    ai_service = get_ai_client()
    groq_client = ai_service.get_client()
    
    if not groq_client:
        if ai_service.config_error == "Missing configuration":
            return "Missing configuration"
        return "Model unavailable"
    
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    
    messages.append({"role": "user", "content": f"{context}{prompt}"})
    current_model = ai_service.router.get_current_model()
    
    try:
        response = groq_client.chat.completions.create(
            model=current_model,
            messages=messages,
            temperature=ai_settings.temperature,
            max_tokens=ai_settings.max_output_tokens
        )
        if not response.choices or not response.choices[0].message.content:
            return "Empty response"
        return response.choices[0].message.content
    except groq.APIStatusError as e:
        code = e.status_code
        if code in (404, 429):
            logger.warning(f"Model {current_model} failed with {code}, marking as failed to use fallback.")
            ai_service.router.mark_failed(current_model)
            ai_service.is_configured = False # Force re-config to select new model
            raise e # Tenacity will retry with the newly selected model
        elif code and code >= 500:
            raise e  # Allow tenacity to handle the retry on the same model
        else:
            return map_groq_error(e)
    except (groq.APIConnectionError, groq.APIError) as e:
        raise e  # Allow tenacity to handle the retry
    except Exception as e:
        return map_groq_error(e)

def generate_response(prompt: str, system_instruction: str = "") -> str:
    """Wrapper to handle RetryError gracefully."""
    if not validate_request_parameters(prompt):
        raise AIError("Empty response")

    target_lang = st.session_state.get("language", "English")
    if target_lang != "English":
        system_instruction = (system_instruction or "") + f"\nIMPORTANT: You must respond/write in {target_lang}."

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
        raise AIError(map_groq_error(last_exc))
    except AIError:
        raise
    except Exception as e:
        raise AIError(map_groq_error(e))

@get_retry_decorator()
@track_time
def _get_stream_and_first_chunk(prompt: str, system_instruction: str = "", context: str = ""):
    ai_service = get_ai_client()
    groq_client = ai_service.get_client()
    
    if not groq_client:
        if ai_service.config_error == "Missing configuration":
            return "Missing configuration", None
        else:
            return "Model unavailable", None
        
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    
    messages.append({"role": "user", "content": f"{context}{prompt}"})
    current_model = ai_service.router.get_current_model()
    
    try:
        response = groq_client.chat.completions.create(
            model=current_model,
            messages=messages,
            temperature=ai_settings.temperature,
            max_tokens=ai_settings.max_output_tokens,
            stream=True
        )
        
        stream = iter(response)
        first_chunk = ""
        while not first_chunk:
            try:
                chunk_obj = next(stream)
                content = chunk_obj.choices[0].delta.content if chunk_obj.choices and chunk_obj.choices[0].delta.content else ""
                first_chunk = content
            except StopIteration:
                break
                
        if not first_chunk:
            return "Empty response", stream
            
        return first_chunk, stream
    except groq.APIStatusError as e:
        code = e.status_code
        if code in (404, 429):
            logger.warning(f"Model {current_model} failed with {code}, marking as failed to use fallback.")
            ai_service.router.mark_failed(current_model)
            ai_service.is_configured = False
            raise e
        raise e
    except (groq.APIConnectionError, groq.APIError) as e:
        raise e
    except Exception as e:
        raise e

def generate_response_stream(prompt: str, system_instruction: str = "") -> Generator[str, None, None]:
    """Generates a streaming response for interactive chat UIs."""
    if not validate_request_parameters(prompt):
        raise AIError("Empty response")

    target_lang = st.session_state.get("language", "English")
    if target_lang != "English":
        system_instruction = (system_instruction or "") + f"\nIMPORTANT: You must respond/write in {target_lang}."

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
                    content = chunk.choices[0].delta.content if chunk.choices and chunk.choices[0].delta.content else ""
                    if content:
                        yield content
                except ValueError:
                    pass

    except StopIteration:
        pass
    except RetryError as e:
        last_exc = e.last_attempt.exception() if e.last_attempt else None
        raise AIError(map_groq_error(last_exc))
    except AIError:
        raise
    except Exception as e:
        raise AIError(map_groq_error(e))

@ai_cache
def translate_text(text: str, target_language: str) -> str:
    """Translates text using Groq."""
    prompt = f"Translate the following text to {target_language}. Return ONLY the translation, no extra text. Do not add any introductory phrases, explanations, or quotes. Just output the translated text.\n\n{text}"
    try:
        return _generate_response_inner(prompt)
    except Exception:
        return generate_response(prompt)

@ai_cache
def generate_emergency_sop(incident_type: str, location: str) -> str:
    """Generates an Emergency Standard Operating Procedure."""
    prompt = f"Generate a concise, 5-step Emergency Standard Operating Procedure (SOP) for a {incident_type} incident at {location} in a busy stadium."
    return generate_response(prompt, system_instruction=Prompts.SYSTEM_EMERGENCY_SOP)
