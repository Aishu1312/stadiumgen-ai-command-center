import streamlit as st
from components.ui import render_header
from utils.data_simulator import generate_incidents
from ai.gemini_client import generate_emergency_sop

st.set_page_config(page_title="Emergency Center", page_icon="🚑", layout="wide")

render_header("Emergency AI Command", "Live incident tracking and automated SOP generation")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🚨 Active Incidents")
    df_incidents = generate_incidents()
    
    st.dataframe(
        df_incidents.style.applymap(
            lambda x: 'background-color: rgba(239, 68, 68, 0.2); color: #f87171;' if x == 'Pending' else 
                      'background-color: rgba(16, 185, 129, 0.2); color: #34d399;' if x == 'Resolved' else 
                      'background-color: rgba(245, 158, 11, 0.2); color: #fbbf24;',
            subset=['Status']
        ),
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.markdown("### 📜 Generate AI SOP")
    incident_type = st.selectbox("Incident Type:", ["Medical Emergency", "Fire", "Lost Child", "Security Threat", "Crowd Panic"])
    location = st.text_input("Location:", placeholder="e.g., Gate 4, Section 102")
    
    if st.button("Generate Action Checklist", type="primary"):
        if location:
            with st.spinner("AI is generating Emergency SOP..."):
                sop = generate_emergency_sop(incident_type, location)
                st.error("🚨 EMERGENCY SOP GENERATED 🚨")
                st.write(sop)
        else:
            st.warning("Please provide a location to generate the SOP.")
