import streamlit as st
from config.settings import settings

def init_session_state():
    """Initializes global session state variables to prevent KeyErrors."""
    if "theme" not in st.session_state:
        st.session_state.theme = "Dark Mode (Glassmorphism)"
    if "language" not in st.session_state:
        st.session_state.language = settings.DEFAULT_LANGUAGE
    if "messages" not in st.session_state:
        st.session_state.messages = []
