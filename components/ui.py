import streamlit as st

def load_css(file_path):
    """Loads a CSS file and injects it into the Streamlit app."""
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found at {file_path}")

def render_glass_card(content_html, height=None):
    """Renders a div with glassmorphism styling containing HTML content."""
    style = f"height: {height}px;" if height else ""
    st.markdown(
        f"""
        <div class="glass-card" style="{style}">
            {content_html}
        </div>
        """,
        unsafe_allow_html=True
    )

def render_metric(label, value, trend=None, trend_color="success"):
    """Renders a beautiful metric card."""
    trend_html = ""
    if trend:
        trend_html = f'<div class="badge badge-{trend_color}" style="margin-top: 10px;">{trend}</div>'
    
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

def render_header(title, subtitle=None):
    """Renders a styled header for pages."""
    st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p style='color: #94a3b8; font-size: 1.1rem;'>{subtitle}</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
