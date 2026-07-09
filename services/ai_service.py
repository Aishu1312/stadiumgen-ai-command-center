import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings
from config.constants import Prompts
from typing import Generator, Any, Optional

load_dotenv()

def get_genai_model() -> Optional[Any]:
    """Initializes the Gemini model."""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    except Exception:
        api_key = os.getenv("GEMINI_API_KEY")

    if api_key and api_key != "your_gemini_api_key_here":
        genai.configure(api_key=api_key)
        # Apply strict generation config
        generation_config = {
            "temperature": settings.TEMPERATURE,
            "max_output_tokens": settings.MAX_OUTPUT_TOKENS,
        }
        return genai.GenerativeModel(
            model_name=settings.DEFAULT_MODEL,
            generation_config=generation_config
        )
    return None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_response(prompt: str, system_instruction: str = "") -> str:
    """Generates a text response from Gemini given a prompt with retry logic."""
    model = get_genai_model()
    if not model:
        return "[Simulated AI Response]: Please configure the GEMINI_API_KEY to enable live AI responses. \n\n" + prompt[:100]
    
    full_prompt = f"System: {system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_response_stream(prompt: str, system_instruction: str = "") -> Generator[str, None, None]:
    """Generates a streaming response for interactive chat UIs."""
    model = get_genai_model()
    if not model:
        yield "[Simulated AI Response]: Please configure the GEMINI_API_KEY.\n\n"
        yield prompt[:50] + "..."
        return
        
    full_prompt = f"System: {system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
    try:
        response = model.generate_content(full_prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"\n\n[Error]: {str(e)}"

def translate_text(text: str, target_language: str) -> str:
    """Translates text using Gemini."""
    prompt = f"Translate the following text to {target_language}. Return ONLY the translation, no extra text.\n\n{text}"
    return generate_response(prompt)

def generate_emergency_sop(incident_type: str, location: str) -> str:
    """Generates an Emergency Standard Operating Procedure."""
    prompt = f"Generate a concise, 5-step Emergency Standard Operating Procedure (SOP) for a {incident_type} incident at {location} in a busy stadium."
    return generate_response(prompt, system_instruction=Prompts.SYSTEM_EMERGENCY_SOP)
