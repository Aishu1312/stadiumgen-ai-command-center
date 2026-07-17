import streamlit as st
from components.ui import render_header, render_toast
from config.settings import settings

st.session_state.current_page_context = "User is on the Settings page configuring application preferences."

def display_settings():
    render_header("System Settings", "Configure application preferences and AI models")

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🌍 Language Preferences")
        
        languages_map = {
            "English": "English",
            "Spanish": "Español",
            "French": "Français",
            "Arabic": "العربية",
            "Portuguese": "Português",
            "Hindi": "हिन्दी",
            "Japanese": "日本語",
            "German": "Deutsch",
            "Italian": "Italiano",
            "Chinese": "中文"
        }
        reverse_languages_map = {v: k for k, v in languages_map.items()}
        
        current_lang = st.session_state.get("language", "English")
        native_options = list(languages_map.values())
        default_native = languages_map.get(current_lang, "English")
        try:
            default_index = native_options.index(default_native)
        except ValueError:
            default_index = 0
            
        selected_native = st.selectbox("Default Application Language", 
                     native_options,
                     index=default_index)
        lang = reverse_languages_map.get(selected_native, "English")
        
        st.markdown("### 🤖 AI Configuration")
        st.selectbox("LLM Provider", ["Groq (Preferred)", "OpenAI", "Anthropic"])
        from config.ai_config import ai_settings
        st.slider("AI Creativity (Temperature)", min_value=0.0, max_value=1.0, value=ai_settings.temperature, step=0.1)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🎨 Theme Settings")
        
        theme_options = ["Dark Mode (Glassmorphism)", "Light Mode"]
        current_theme = st.session_state.get("theme", "Dark Mode (Glassmorphism)")
        try:
            theme_index = theme_options.index(current_theme)
        except ValueError:
            theme_index = 0
        theme = st.radio("Active Theme", theme_options, index=theme_index)

        st.markdown("### 🔐 Security")
        st.checkbox("Enable Offline Emergency Mode", value=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Save Settings", type="primary", use_container_width=True):
        st.session_state.language = lang
        st.session_state.theme = theme
        st.success("Settings saved successfully.")
        render_toast("Settings updated", "⚙️")
        st.rerun()

display_settings()
