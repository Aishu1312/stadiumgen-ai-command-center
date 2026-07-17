import streamlit as st
import os

# Page Config MUST be the very first Streamlit command
st.set_page_config(
    page_title="WorldCup AI Command Center",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize translation layer
from utils.translation import initialize_translation
initialize_translation()

from components.ui import load_css
from utils.session import init_session_state
from config.settings import settings

def main():
    if not settings.api_key_resolved:
        st.error("🚨 **Configuration Error: Missing API Key**")
        st.markdown("The application requires a `GROQ_API_KEY` to function.")
        st.markdown("Please set it in your `.env` file or Streamlit secrets.")
        st.stop()
        
    init_session_state()
    
    # Ensure style.css is loaded globally
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(current_dir, "assets", "style.css")
    load_css(css_path)
    
    # Load CSS theme override if Light Mode is selected
    if st.session_state.get("theme") == "Light Mode":
        st.markdown(
            """
            <style>
            :root {
                --background: #f8fafc !important;
                --surface: rgba(255, 255, 255, 0.85) !important;
                --surface-hover: rgba(255, 255, 255, 0.95) !important;
                --text-main: #0f172a !important;
                --text-muted: #334155 !important;
            }
            .stApp {
                background: radial-gradient(circle at top left, #f1f5f9, var(--background)) !important;
                color: var(--text-main) !important;
            }
            /* Global text elements in the app */
            .stApp p, 
            .stApp span:not(.badge), 
            .stApp label, 
            .stApp li, 
            .stApp td, 
            .stApp th, 
            .stApp small, 
            .stApp legend,
            .stApp h1, 
            .stApp h2, 
            .stApp h3, 
            .stApp h4, 
            .stApp h5, 
            .stApp h6 {
                color: var(--text-main) !important;
            }
            
            /* Sidebar styling overrides */
            [data-testid="stSidebar"] {
                background: rgba(241, 245, 249, 0.9) !important;
                border-right: 1px solid rgba(0, 0, 0, 0.08) !important;
            }
            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] span,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] li,
            [data-testid="stSidebar"] div {
                color: #0f172a !important;
            }
            
            /* Input controls */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > div,
            .stTextArea > div > div > textarea,
            .stNumberInput > div > div > input {
                background-color: rgba(255, 255, 255, 0.95) !important;
                border: 1px solid rgba(0, 0, 0, 0.15) !important;
                color: #0f172a !important;
            }
            
            /* Chat Input */
            div[data-testid="stChatInput"] textarea {
                color: #0f172a !important;
                background-color: #ffffff !important;
                border: 1px solid rgba(0, 0, 0, 0.15) !important;
            }
            
            /* Selectbox overlays and dropdown menus */
            div[data-baseweb="popover"] *,
            div[data-baseweb="menu"] *,
            div[role="listbox"] *,
            div[role="option"] * {
                color: #0f172a !important;
                background-color: #ffffff !important;
            }
            div[data-baseweb="popover"] div:hover,
            div[data-baseweb="menu"] div:hover,
            div[role="listbox"] div:hover,
            div[role="option"]:hover {
                background-color: #f1f5f9 !important;
            }
            
            /* Metric values and labels overrides */
            .metric-value {
                background: -webkit-linear-gradient(45deg, #0f172a, var(--primary)) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
            }
            .metric-label {
                color: var(--text-muted) !important;
            }
            
            /* Divider lines */
            .styled-hr {
                background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.15), rgba(0, 0, 0, 0)) !important;
            }
            
            /* Cards styling in Light Mode */
            .glass-card {
                background: var(--surface) !important;
                border: 1px solid rgba(0, 0, 0, 0.08) !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important;
            }
            .glass-card:hover {
                background: var(--surface-hover) !important;
                box-shadow: 0 15px 40px rgba(0, 0, 0, 0.08) !important;
                border-color: rgba(0, 0, 0, 0.12) !important;
            }
            
            /* Table formatting */
            .stDataFrame div {
                color: #0f172a !important;
            }
            
            /* Exclude alert notifications from the general color override */
            .stApp div[data-testid="stAlert"] p,
            .stApp div[data-testid="stAlert"] span,
            .stApp div[data-testid="stAlert"] li,
            .stApp div[data-testid="stAlert"] div {
                color: inherit !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    
    # Define pages for navigation
    pages = {
        "Main": [
            st.Page("views/home.py", title="Home", icon="🏠", default=True),
            st.Page("views/ai_assistant.py", title="AI Assistant", icon="🤖"),
        ],
        "Operations": [
            st.Page("views/smart_navigation.py", title="Smart Navigation", icon="🗺️"),
            st.Page("views/crowd_intelligence.py", title="Crowd Intelligence", icon="👥"),
            st.Page("views/transport.py", title="Transport Planner", icon="🚍"),
            st.Page("views/emergency_center.py", title="Emergency Center", icon="🚑"),
        ],
        "Management": [
            st.Page("views/organizer_dashboard.py", title="Organizer Dashboard", icon="📊"),
            st.Page("views/sustainability.py", title="Sustainability", icon="🌱"),
            st.Page("views/accessibility.py", title="Accessibility", icon="♿"),
        ],
        "System": [
            st.Page("views/settings.py", title="Settings", icon="⚙️"),
        ]
    }

    # Initialize navigation
    pg = st.navigation(pages)
    
    # Sidebar Global Elements
    with st.sidebar:
        st.markdown(f"## {settings.APP_NAME} ⚽")
        st.markdown(f"**Version**: {settings.APP_VERSION}")
        st.markdown("---")
        st.info("💡 **Tip**: Use the AI Assistant for quick insights on any page.")

    # Run the selected page
    try:
        pg.run()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.exception(e)

if __name__ == "__main__":
    main()
# Force reload
# Reload again
# Force reload again
# Bumping cache
# Bust cache again

# Bump cache# Bust cache Phase 6
# Bust cache Phase 7
# Bust cache Phase 8
# Bust cache Phase 9
