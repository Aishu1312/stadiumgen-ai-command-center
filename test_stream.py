import os
import sys

# setup dummy streamlit
import streamlit as st
st.secrets = {}
st.session_state = {}

from config.settings import settings
from services.ai_service import generate_response_stream

metrics = {'energy_saved_kwh': 1348, 'plastic_recycled_kg': 1200, 'carbon_offset_tons': 3.5, 'water_saved_liters': 10000}
prompt = f"Write a short, encouraging sustainability report for the stadium operations based on these metrics: {metrics}. Suggest 2 actionable ways to improve further."

print("Starting stream...")
stream = generate_response_stream(prompt)
for chunk in stream:
    print("CHUNK:", repr(chunk))
