import streamlit as st
from components.ui import render_header
from utils.data_simulator import generate_transport_data
from ai.gemini_client import generate_response

st.set_page_config(page_title="AI Transport Planner", page_icon="🚍", layout="wide")

render_header("AI Transportation Planner", "Predictive routing and live transit status")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🚏 Live Transport Status")
    df_transport = generate_transport_data()
    st.dataframe(
        df_transport.style.applymap(
            lambda x: 'background-color: rgba(239, 68, 68, 0.2); color: #f87171;' if x == 'Delayed' else 
                      'background-color: rgba(16, 185, 129, 0.2); color: #34d399;' if x == 'On Time' else 
                      'background-color: rgba(245, 158, 11, 0.2); color: #fbbf24;',
            subset=['Status']
        ),
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.markdown("### 🤖 Ask AI for Travel Advice")
    user_loc = st.text_input("Your Location:", placeholder="e.g., Downtown Hotel")
    
    if st.button("Generate Route Recommendation"):
        if user_loc:
            with st.spinner("AI is analyzing traffic, carbon impact, and transit schedules..."):
                prompt = f"Provide a travel recommendation from {user_loc} to the World Cup Stadium. Suggest the fastest route, the most eco-friendly route, and expected travel time."
                recommendation = generate_response(prompt)
                st.success("Recommendation Ready!")
                st.write(recommendation)
        else:
            st.warning("Please enter your location.")
