import pandas as pd
import random
import datetime
import streamlit as st
from typing import List, Dict, Any
from config.constants import Constants
from models.data_models import CrowdZone, TransportRoute, Incident, SustainabilityMetrics

@st.cache_data(ttl=60)
def generate_crowd_data() -> pd.DataFrame:
    """Generates simulated crowd density data. Cached for 60s."""
    data = []
    for zone in Constants.ZONES:
        occupancy = random.randint(30, 100)
        status = "Green" if occupancy < 60 else "Yellow" if occupancy < 80 else "Orange" if occupancy < 95 else "Red"
        data.append({
            "Zone": zone,
            "Occupancy %": occupancy,
            "Status": status,
            "Estimated Wait (mins)": random.randint(2, 30) if occupancy > 50 else random.randint(0, 5)
        })
    return pd.DataFrame(data)

@st.cache_data(ttl=120)
def generate_transport_data() -> pd.DataFrame:
    """Generates simulated transport data. Cached for 120s."""
    data = []
    for route in Constants.ROUTES:
        delay = random.randint(0, 20)
        status = "On Time" if delay == 0 else "Slight Delay" if delay < 10 else "Delayed"
        data.append({
            "Service": route,
            "Status": status,
            "Delay (mins)": delay,
            "Crowd Level": random.choice(["Low", "Medium", "High", "Critical"])
        })
    return pd.DataFrame(data)

@st.cache_data(ttl=300)
def generate_incidents() -> pd.DataFrame:
    """Generates recent simulated incidents. Cached for 300s."""
    incidents = []
    for _ in range(5):
        incidents.append({
            "Time": (datetime.datetime.now() - datetime.timedelta(minutes=random.randint(1, 60))).strftime("%H:%M"),
            "Type": random.choice(Constants.INCIDENT_TYPES),
            "Location": random.choice(["Gate 4", "Section 102", "Restroom B", "North Concourse", "VIP Entry"]),
            "Status": random.choice(["Resolved", "In Progress", "Pending"])
        })
    return pd.DataFrame(incidents)

@st.cache_data(ttl=300)
def generate_sustainability_metrics() -> Dict[str, Any]:
    """Generates simulated sustainability metrics."""
    return {
        "energy_saved_kwh": random.randint(1000, 5000),
        "plastic_recycled_kg": random.randint(500, 2000),
        "carbon_offset_tons": random.uniform(1.5, 5.0),
        "water_saved_liters": random.randint(5000, 15000)
    }

@st.cache_data(ttl=600)
def generate_map_data() -> pd.DataFrame:
    """Generates dummy lat/lon data for map visualizations near a stadium."""
    base_lat = 40.8128
    base_lon = -74.0742
    
    data = []
    for _ in range(50):
        data.append({
            "lat": base_lat + random.uniform(-0.01, 0.01),
            "lon": base_lon + random.uniform(-0.01, 0.01),
            "density": random.uniform(0, 1)
        })
    return pd.DataFrame(data)
