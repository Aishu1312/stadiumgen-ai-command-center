import streamlit as st
from components.ui import render_header, render_metric
from utils.data_simulator import generate_sustainability_metrics
from ai.gemini_client import generate_response

st.set_page_config(page_title="Sustainability", page_icon="🌱", layout="wide")

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

st.markdown("---")
st.markdown("### 📝 AI Sustainability Report Generator")
if st.button("Generate Today's Green Report"):
    with st.spinner("AI is analyzing today's metrics to generate a report..."):
        prompt = f"Write a short, encouraging sustainability report for the stadium operations based on these metrics: {metrics}. Suggest 2 actionable ways to improve further."
        report = generate_response(prompt)
        st.markdown(f"> {report}")
