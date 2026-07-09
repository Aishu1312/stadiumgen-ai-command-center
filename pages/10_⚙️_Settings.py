import streamlit as st
from components.ui import render_header

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

render_header("System Settings", "Configure application preferences and AI models")

st.markdown("### 🌍 Language Preferences")
st.selectbox("Default Application Language", ["English", "Spanish", "French", "Arabic", "Portuguese", "Hindi", "Japanese", "German", "Italian", "Chinese"])

st.markdown("### 🤖 AI Configuration")
st.selectbox("LLM Provider", ["Google Gemini (Preferred)", "OpenAI", "Anthropic"])
st.slider("AI Creativity (Temperature)", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

st.markdown("### 🎨 Theme Settings")
st.radio("Active Theme", ["Dark Mode (Glassmorphism)", "Light Mode"])

st.markdown("### 🔐 Security")
st.checkbox("Enable Offline Emergency Mode", value=True)
st.checkbox("Auto-dispatch Security on Red Zones", value=False)

st.success("Settings saved successfully.")
