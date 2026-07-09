import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure API
try:
    API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
except Exception:
    API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY and API_KEY != "your_gemini_api_key_here":
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro') # Using latest model
else:
    model = None

def generate_response(prompt, system_instruction=None):
    """Generates a response from Gemini given a prompt."""
    if not model:
        return "[Simulated AI Response]: Please configure the GEMINI_API_KEY in the .env file to enable live AI responses. \n\nBased on your prompt, here is a mock generated response: " + prompt[:50] + "..."
    
    try:
        # Note: Depending on the generativeai version, system instructions can be passed differently.
        # For simplicity, we prepend it to the prompt if provided.
        full_prompt = f"System: {system_instruction}\n\nUser: {prompt}" if system_instruction else prompt
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"

def translate_text(text, target_language):
    """Translates text using Gemini."""
    prompt = f"Translate the following text to {target_language}. Return ONLY the translation, no extra text.\n\n{text}"
    return generate_response(prompt)

def generate_emergency_sop(incident_type, location):
    """Generates an Emergency Standard Operating Procedure."""
    prompt = f"Generate a concise, 5-step Emergency Standard Operating Procedure (SOP) for a {incident_type} incident at {location} in a busy stadium. Format with bullet points."
    return generate_response(prompt)
