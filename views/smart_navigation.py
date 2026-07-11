import streamlit as st
from components.ui import render_header, show_loading_skeleton, render_toast

st.session_state.current_page_context = "User is currently on the Smart Navigation page, routing between stadium zones."

def display_navigation():
    render_header("AI Indoor Navigation", "Find the shortest and most accessible routes")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📍 Directions")
        start = st.selectbox("From:", ["Gate 1", "Gate 2", "VIP Entrance", "Metro Station", "Parking Lot A"])
        destination = st.selectbox("To:", ["Section 102", "Food Court B", "Medical Room 1", "Restroom A", "VIP Lounge"])
        
        needs_wheelchair = st.checkbox("♿ Wheelchair Accessible Route")
        
        if st.button("Find Route", use_container_width=True):
            show_loading_skeleton(1.5, "AI is calculating the optimal route...")
            st.success(f"Route found from {start} to {destination}!")
            st.info("Estimated walking time: 5 mins")
            if needs_wheelchair:
                st.warning("Note: Route includes elevators at Concourse B.")
            render_toast("Route calculation complete.", "📍")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("### 🏟️ Interactive Map")
        try:
            import folium
            from streamlit_folium import st_folium
            m = folium.Map(location=[40.8128, -74.0742], zoom_start=16, tiles="CartoDB dark_matter")
            folium.Marker([40.8128, -74.0742], popup="Stadium Center", icon=folium.Icon(color="blue", icon="info-sign")).add_to(m)
            folium.Marker([40.8140, -74.0750], popup="Gate 1", icon=folium.Icon(color="green", icon="play")).add_to(m)
            
            st_folium(m, width="100%", height=500, returned_objects=[])
        except ImportError:
            st.error("Missing dependency: folium. Please ensure requirements are installed.")

display_navigation()
