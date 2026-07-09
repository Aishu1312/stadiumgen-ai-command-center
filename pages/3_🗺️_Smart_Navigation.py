import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from components.ui import render_header

st.set_page_config(page_title="Smart Navigation", page_icon="🗺️", layout="wide")

render_header("AI Indoor Navigation", "Find the shortest and most accessible routes")

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### 📍 Directions")
    start = st.selectbox("From:", ["Gate 1", "Gate 2", "VIP Entrance", "Metro Station", "Parking Lot A"])
    destination = st.selectbox("To:", ["Section 102", "Food Court B", "Medical Room 1", "Restroom A", "VIP Lounge"])
    
    needs_wheelchair = st.checkbox("♿ Wheelchair Accessible Route")
    
    if st.button("Find Route", use_container_width=True):
        with st.spinner("AI is calculating the optimal route..."):
            st.success(f"Route found from {start} to {destination}!")
            st.info("Estimated walking time: 5 mins")
            if needs_wheelchair:
                st.warning("Note: Route includes elevators at Concourse B.")

with col2:
    st.markdown("### 🏟️ Interactive Map")
    
    # Create a dummy map centered on a stadium (MetLife Stadium coords)
    m = folium.Map(location=[40.8128, -74.0742], zoom_start=16, tiles="CartoDB dark_matter")
    
    # Add dummy route and markers
    folium.Marker([40.8128, -74.0742], popup="Stadium Center", icon=folium.Icon(color="blue", icon="info-sign")).add_to(m)
    folium.Marker([40.8140, -74.0750], popup="Gate 1", icon=folium.Icon(color="green", icon="play")).add_to(m)
    
    st_folium(m, width=800, height=500)
