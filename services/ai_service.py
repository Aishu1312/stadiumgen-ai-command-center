import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings
from config.constants import Prompts
from typing import Generator, Any, Optional
import logging

load_dotenv()
logger = logging.getLogger(__name__)

@st.cache_resource
def get_genai_model() -> Optional[Any]:
    """Initializes the Gemini model safely without hardcoded keys."""
    api_key = os.environ.get("GEMINI_API_KEY")
    
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
        
    if not api_key or api_key.strip() == "" or api_key == "your_gemini_api_key_here":
        logger.warning("Gemini API key is missing.")
        return None

    try:
        genai.configure(api_key=api_key)
        generation_config = {
            "temperature": settings.TEMPERATURE,
            "max_output_tokens": settings.MAX_OUTPUT_TOKENS,
        }
        return genai.GenerativeModel(
            model_name=settings.DEFAULT_MODEL,
            generation_config=generation_config
        )
    except Exception as e:
        logger.error(f"Failed to configure Gemini model: {e}")
        return None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_response(prompt: str, system_instruction: str = "") -> str:
    """Generates a text response from Gemini given a prompt with retry logic."""
    model = get_genai_model()
    if not model:
        return "[Simulated AI Response] The GEMINI_API_KEY is not configured in Secrets or .env. Please add it to use real AI functionality.\n\nSimulated output for: " + prompt[:100]
    
    # Optional context from current page
    context = ""
    if hasattr(st.session_state, "current_page_context"):
        context = f"Current Context: {st.session_state.current_page_context}\n\n"
        
    full_prompt = f"System: {system_instruction}\n{context}\nUser: {prompt}" if system_instruction else f"{context}{prompt}"
    
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error in generate_response: {e}")
        return f"🚨 Error communicating with AI: {str(e)}. Please check your API limits or network connection."

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_response_stream(prompt: str, system_instruction: str = "") -> Generator[str, None, None]:
    """Generates a streaming response for interactive chat UIs."""
    model = get_genai_model()
    if not model:
        yield "[Simulated AI Response] The GEMINI_API_KEY is not configured.\n\n"
        yield "Please configure it in the Streamlit Cloud Secrets or local .env file."
        return
        
    # Inject current page context
    context = ""
    if hasattr(st.session_state, "current_page_context"):
        context = f"Current Context: {st.session_state.current_page_context}\n\n"

    full_prompt = f"System: {system_instruction}\n{context}\nUser: {prompt}" if system_instruction else f"{context}{prompt}"
    
    try:
        response = model.generate_content(full_prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        logger.error(f"Error in generate_response_stream: {e}")
        yield f"\n\n[🚨 Error]: {str(e)}"

def translate_text(text: str, target_language: str) -> str:
    """Translates text using Gemini."""
    prompt = f"Translate the following text to {target_language}. Return ONLY the translation, no extra text.\n\n{text}"
    return generate_response(prompt)

def generate_emergency_sop(incident_type: str, location: str) -> str:
    """Generates an Emergency Standard Operating Procedure."""
    prompt = f"Generate a concise, 5-step Emergency Standard Operating Procedure (SOP) for a {incident_type} incident at {location} in a busy stadium."
    return generate_response(prompt, system_instruction=Prompts.SYSTEM_EMERGENCY_SOP)
