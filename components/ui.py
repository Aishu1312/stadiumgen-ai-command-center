import streamlit as st
import time

def load_css(file_path: str):
    """Loads a CSS file and injects it into the Streamlit app."""
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file not found at {file_path}")

def render_metric(label: str, value: str, trend: str = None, trend_color: str = "success"):
    """Renders a beautiful metric card with hover effects."""
    trend_html = ""
    if trend:
        trend_html = f'<div class="badge badge-{trend_color}" style="margin-top: 8px;">{trend}</div>'
    
    st.markdown(
        f"""
        <div class="glass-card metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {trend_html}
        </div>
        """,
        unsafe_allow_html=True
    )

def render_header(title: str, subtitle: str = None):
    """Renders a styled header for pages with gradient text."""
    st.markdown(f"<h1 class='gradient-text'>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p class='subtitle'>{subtitle}</p>", unsafe_allow_html=True)
    st.markdown("<hr class='styled-hr'>", unsafe_allow_html=True)

def show_loading_skeleton(seconds: float = 1.0, message: str = "Loading data..."):
    """Displays a skeleton loading state using Streamlit's native spinner."""
    with st.spinner(message):
        time.sleep(seconds)

def render_toast(message: str, icon: str = "ℹ️"):
    """Displays a toast notification."""
    st.toast(message, icon=icon)
