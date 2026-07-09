import streamlit as st
from components.ui import render_header, render_metric, show_loading_skeleton, render_toast
from services.data_service import generate_sustainability_metrics
from services.ai_service import generate_response_stream

st.set_page_config(page_title="Sustainability", page_icon="🌱", layout="wide")

def display_sustainability():
    render_header("Sustainability Intelligence", "Monitoring eco-friendly operations in real-time")

    metrics = generate_sustainability_metrics()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric("Energy Saved", f"{metrics['energy_saved_kwh']} kWh", "+12% vs yesterday", "success")
    with col2:
        render_metric("Plastic Recycled", f"{metrics['plastic_recycled_kg']} kg", "+5%", "success")
    with col3:
        render_metric("Carbon Offset", f"{metrics['carbon_offset_tons']:.1f} tons", "On target", "info")
    with col4:
        render_metric("Water Saved", f"{metrics['water_saved_liters']} L", "-2% drop", "warning")

    st.markdown("<hr class='styled-hr'>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📝 AI Sustainability Report Generator")
    if st.button("Generate Today's Green Report", use_container_width=True):
        st.markdown("#### Generated Report")
        prompt = f"Write a short, encouraging sustainability report for the stadium operations based on these metrics: {metrics}. Suggest 2 actionable ways to improve further."
        
        stream = generate_response_stream(prompt)
        st.write_stream(stream)
        render_toast("Green Report Generated", "🌱")
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    display_sustainability()
