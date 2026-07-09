import streamlit as st
import os

# Page Config MUST be the very first Streamlit command
st.set_page_config(
    page_title="WorldCup AI Command Center",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

from components.ui import load_css
from config.settings import settings

def init_session_state():
    """Initializes global session state variables to prevent KeyErrors."""
    if "theme" not in st.session_state:
        st.session_state.theme = "Dark Mode (Glassmorphism)"
    if "language" not in st.session_state:
        st.session_state.language = settings.DEFAULT_LANGUAGE
    if "messages" not in st.session_state:
        st.session_state.messages = []

def main():
    init_session_state()
    
    # Ensure style.css is loaded
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(current_dir, "assets", "style.css")
    load_css(css_path)

    st.markdown(f"<h1 style='text-align: center; font-size: 4rem; margin-top: 2rem;' class='gradient-text'>{settings.APP_NAME} ⚽</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #94a3b8;'>The Intelligent Stadium Companion powered by Generative AI</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("assets/hero_image.png", use_column_width=True)
        except Exception:
            st.image("https://images.unsplash.com/photo-1518605368461-1e96f01df22e?q=80&w=800&auto=format&fit=crop", use_column_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align: center;'>
            <p style='font-size: 1.2rem; color: #cbd5e1;'>
                Welcome to the future of stadium management. Use the sidebar to navigate through 
                Smart Navigation, Crowd Intelligence, AI Transport Planner, and more.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info("👈 Please select a module from the sidebar to begin.")

if __name__ == "__main__":
    main()
