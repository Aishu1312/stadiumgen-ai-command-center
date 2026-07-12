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
from utils.session import init_session_state
from config.settings import settings

def main():
    init_session_state()
    
    # Ensure style.css is loaded globally
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(current_dir, "assets", "style.css")
    load_css(css_path)
    
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
