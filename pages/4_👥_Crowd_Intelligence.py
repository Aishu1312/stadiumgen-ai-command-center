import streamlit as st
import plotly.express as px
from components.ui import render_header, render_metric
from services.data_service import generate_crowd_data, generate_map_data

st.set_page_config(page_title="Crowd Intelligence", page_icon="👥", layout="wide")

def display_crowd_dashboard():
    render_header("Crowd Intelligence Dashboard", "Live density tracking and queue predictions")

    df_crowd = generate_crowd_data()

    col1, col2, col3 = st.columns(3)
    total_zones = len(df_crowd)
    red_zones = len(df_crowd[df_crowd["Status"] == "Red"])
    avg_wait = df_crowd["Estimated Wait (mins)"].mean()

    with col1:
        render_metric("Zones Monitored", str(total_zones))
    with col2:
        render_metric("Critical Zones", str(red_zones), "Needs attention" if red_zones > 0 else "All Clear", "danger" if red_zones > 0 else "success")
    with col3:
        render_metric("Avg Wait Time", f"{avg_wait:.1f} mins", "-1.2 mins", "success")

    st.markdown("<hr class='styled-hr'>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### 📊 Zone Occupancy")
        fig = px.bar(
            df_crowd, 
            x="Zone", 
            y="Occupancy %", 
            color="Status",
            color_discrete_map={"Green": "#10b981", "Yellow": "#f59e0b", "Orange": "#f97316", "Red": "#ef4444"},
            template="plotly_dark"
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("### 🔥 Crowd Heatmap")
        df_map = generate_map_data()
        fig_map = px.density_mapbox(
            df_map, lat='lat', lon='lon', z='density', radius=25,
            center=dict(lat=40.8128, lon=-74.0742), zoom=14,
            mapbox_style="carto-darkmatter",
            template="plotly_dark"
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

if __name__ == "__main__":
    display_crowd_dashboard()
