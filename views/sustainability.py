import streamlit as st
from components.ui import render_header, render_metric, show_loading_skeleton, render_toast
from services.data_service import generate_sustainability_metrics
from services.ai_service import generate_response_stream

st.session_state.current_page_context = "User is on the Sustainability page, checking eco-metrics."

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
    
    st.markdown("""
        <div class='glass-card' style='margin-bottom: 15px; padding-bottom: 10px;'>
            <h3 style='margin-bottom: 0;'>📝 AI Sustainability Report Generator</h3>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Generate Today's Green Report", use_container_width=True):
        st.markdown("#### Generated Report")
        prompt = f"""
        Write a highly detailed, professional, and comprehensive sustainability report for the stadium operations based on these metrics: {metrics}.
        
        The report must include exactly the following sections with proper markdown headings and bullet points:
        - Executive Summary
        - Energy Savings
        - Carbon Emission Reduction
        - Water Conservation
        - Waste Management
        - Renewable Energy Usage
        - Attendance Insights
        - Operational Highlights
        - AI Recommendations
        - Future Sustainability Goals
        - Overall Performance Rating
        - Closing Summary
        
        Ensure the report reads naturally from start to finish with no incomplete sentences or truncation.
        """
        
        stream = generate_response_stream(prompt)
        st.write_stream(stream)
        render_toast("Green Report Generated", "🌱")

display_sustainability()
