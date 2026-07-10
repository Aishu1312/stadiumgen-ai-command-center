import streamlit as st

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

from utils.session import init_session_state
init_session_state()
from components.ui import render_header, render_toast
from config.settings import settings


def display_settings():
    render_header("System Settings", "Configure application preferences and AI models")

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🌍 Language Preferences")
        lang = st.selectbox("Default Application Language", 
                     ["English", "Spanish", "French", "Arabic", "Portuguese", "Hindi", "Japanese", "German", "Italian", "Chinese"],
                     index=0)
        
        st.markdown("### 🤖 AI Configuration")
        st.selectbox("LLM Provider", ["Google Gemini (Preferred)", "OpenAI", "Anthropic"])
        st.slider("AI Creativity (Temperature)", min_value=0.0, max_value=1.0, value=settings.TEMPERATURE, step=0.1)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🎨 Theme Settings")
        st.radio("Active Theme", ["Dark Mode (Glassmorphism)", "Light Mode"])

        st.markdown("### 🔐 Security")
        st.checkbox("Enable Offline Emergency Mode", value=True)
        st.checkbox("Auto-dispatch Security on Red Zones", value=False)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Save Settings", type="primary", use_container_width=True):
        st.session_state.language = lang
        st.success("Settings saved successfully.")
        render_toast("Settings updated", "⚙️")

if __name__ == "__main__":
    display_settings()
