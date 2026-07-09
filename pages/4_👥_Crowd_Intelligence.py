import streamlit as st
from components.ui import render_header, render_metric
from utils.data_simulator import generate_crowd_data, generate_map_data
import plotly.express as px

st.set_page_config(page_title="Crowd Intelligence", page_icon="👥", layout="wide")

render_header("Crowd Intelligence Dashboard", "Live density tracking and queue predictions")

df_crowd = generate_crowd_data()

col1, col2, col3 = st.columns(3)
total_zones = len(df_crowd)
red_zones = len(df_crowd[df_crowd["Status"] == "Red"])
avg_wait = df_crowd["Estimated Wait (mins)"].mean()

with col1:
    render_metric("Total Zones Monitored", str(total_zones))
with col2:
    render_metric("Critical Zones (Red)", str(red_zones), "Needs attention" if red_zones > 0 else "All Clear", "danger" if red_zones > 0 else "success")
with col3:
    render_metric("Avg Zone Wait Time", f"{avg_wait:.1f} mins")

st.markdown("---")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### 📊 Zone Occupancy")
    fig = px.bar(
        df_crowd, 
        x="Zone", 
        y="Occupancy %", 
        color="Status",
        color_discrete_map={
            "Green": "#10b981",
            "Yellow": "#f59e0b",
            "Orange": "#f97316",
            "Red": "#ef4444"
        },
        template="plotly_dark"
    )
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown("### 🔥 Simulated Crowd Heatmap")
    df_map = generate_map_data()
    fig_map = px.density_mapbox(
        df_map, lat='lat', lon='lon', z='density', radius=20,
        center=dict(lat=40.8128, lon=-74.0742), zoom=14,
        mapbox_style="carto-darkmatter",
        template="plotly_dark"
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
