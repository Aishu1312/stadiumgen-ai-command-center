import pandas as pd
import numpy as np
import datetime
import random
from faker import Faker

fake = Faker()

def generate_crowd_data():
    """Generates simulated crowd density data for different stadium zones."""
    zones = ["North Stand", "South Stand", "East Stand", "West Stand", "VIP Lounge", "Food Court A", "Food Court B", "Fan Zone"]
    data = []
    for zone in zones:
        occupancy = random.randint(30, 100)
        status = "Green" if occupancy < 60 else "Yellow" if occupancy < 80 else "Orange" if occupancy < 95 else "Red"
        data.append({
            "Zone": zone,
            "Occupancy %": occupancy,
            "Status": status,
            "Estimated Wait (mins)": random.randint(2, 30) if occupancy > 50 else random.randint(0, 5)
        })
    return pd.DataFrame(data)

def generate_transport_data():
    """Generates simulated transport data."""
    routes = ["Metro Line A", "Metro Line B", "Bus 101", "Bus 102", "Uber/Lyft Hub"]
    data = []
    for route in routes:
        delay = random.randint(0, 20)
        status = "On Time" if delay == 0 else "Slight Delay" if delay < 10 else "Delayed"
        data.append({
            "Service": route,
            "Status": status,
            "Delay (mins)": delay,
            "Crowd Level": random.choice(["Low", "Medium", "High", "Critical"])
        })
    return pd.DataFrame(data)

def generate_incidents():
    """Generates recent simulated incidents."""
    incident_types = ["Medical", "Lost Child", "Security", "Maintenance"]
    incidents = []
    for _ in range(5):
        incidents.append({
            "Time": (datetime.datetime.now() - datetime.timedelta(minutes=random.randint(1, 60))).strftime("%H:%M"),
            "Type": random.choice(incident_types),
            "Location": random.choice(["Gate 4", "Section 102", "Restroom B", "North Concourse", "VIP Entry"]),
            "Status": random.choice(["Resolved", "In Progress", "Pending"])
        })
    return pd.DataFrame(incidents)

def generate_sustainability_metrics():
    """Generates simulated sustainability metrics."""
    return {
        "energy_saved_kwh": random.randint(1000, 5000),
        "plastic_recycled_kg": random.randint(500, 2000),
        "carbon_offset_tons": random.uniform(1.5, 5.0),
        "water_saved_liters": random.randint(5000, 15000)
    }

def generate_map_data():
    """Generates dummy lat/lon data for map visualizations near a stadium."""
    # Base coords: MetLife Stadium approx
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
