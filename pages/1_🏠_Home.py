import streamlit as st
from components.ui import render_header, render_metric
import pandas as pd
import datetime

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

render_header("Stadium Command Center", "Live Overview of WorldCup 2026 Operations")

col1, col2, col3, col4 = st.columns(4)

with col1:
    render_metric("Total Visitors", "84,521", "+2,100 since last hour", "success")
with col2:
    render_metric("Active Incidents", "3", "-2 resolved recently", "info")
with col3:
    render_metric("Avg Queue Time", "12 mins", "Normal", "success")
with col4:
    render_metric("Sustainability Score", "92/100", "Excellent", "success")

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("### 🏟️ Quick Actions")
col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    if st.button("Generate Evening Report", use_container_width=True):
        st.success("AI is generating the report...")
with col_b:
    if st.button("Broadcast Announcement", use_container_width=True):
        st.info("Broadcast channel opened.")
with col_c:
    if st.button("Lockdown Protocol", use_container_width=True):
        st.error("Protocol initiated!")
with col_d:
    if st.button("Dispatch Medics", use_container_width=True):
        st.warning("Medics dispatched to Zone A.")
