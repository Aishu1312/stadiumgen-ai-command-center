import streamlit as st
import os

# Page Config must be the first Streamlit command
st.set_page_config(
    page_title="WorldCup AI Command Center",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

from components.ui import load_css
import json

# Ensure style.css is loaded
current_dir = os.path.dirname(os.path.abspath(__file__))
css_path = os.path.join(current_dir, "assets", "style.css")
load_css(css_path)

# Main App Router is handled by Streamlit's native multi-page app feature inside the `pages/` directory.
# But we will use option menu in the sidebar for a better look on the Home page and let the user navigate.
# Actually, since it's a multi-page app, the sidebar is automatically generated from the pages folder.
# We will just show a beautiful landing page here.

from streamlit_lottie import st_lottie
import requests

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

st.markdown("<h1 style='text-align: center; font-size: 4rem; margin-top: 2rem;'>WorldCup AI Command Center ⚽</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #94a3b8;'>The Intelligent Stadium Companion powered by Generative AI</h3>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Use a dummy lottie animation url for a globe or stadium
    lottie_url = "https://assets9.lottiefiles.com/packages/lf20_U6OKyGtJzE.json"
    lottie_json = load_lottieurl(lottie_url)
    if lottie_json:
        st_lottie(lottie_json, height=400, key="stadium_lottie")
    else:
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
