import streamlit as st

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

from utils.session import init_session_state
init_session_state()
from components.ui import render_header, render_metric, show_loading_skeleton, render_toast
from services.data_service import generate_sustainability_metrics
import time


def display_home():
    render_header("Stadium Command Center", "Live Overview of WorldCup 2026 Operations")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric("Total Visitors", "84,521", "+2,100 since last hour", "success")
    with col2:
        render_metric("Active Incidents", "3", "-2 resolved recently", "info")
    with col3:
        render_metric("Avg Queue Time", "12 mins", "Normal", "success")
    with col4:
        score = generate_sustainability_metrics().get("energy_saved_kwh", 0)
        render_metric("Sustainability Score", f"{score/100:.0f}/100", "Excellent", "success")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 🏟️ Quick Actions")
    col_a, col_b, col_c, col_d = st.columns(4)
    
    with col_a:
        if st.button("Generate Evening Report", use_container_width=True):
            show_loading_skeleton(1.5, "Compiling metrics...")
            render_toast("Evening Report generated successfully!", "✅")
            st.success("Report saved to documents.")
    with col_b:
        if st.button("Broadcast Announcement", use_container_width=True):
            render_toast("Broadcast channel opened.", "🔊")
    with col_c:
        if st.button("Lockdown Protocol", use_container_width=True):
            st.error("Protocol initiated!")
            render_toast("CRITICAL: Lockdown engaged.", "🚨")
    with col_d:
        if st.button("Dispatch Medics", use_container_width=True):
            st.warning("Medics dispatched to Zone A.")
            render_toast("Medics en route.", "🚑")

if __name__ == "__main__":
    display_home()
