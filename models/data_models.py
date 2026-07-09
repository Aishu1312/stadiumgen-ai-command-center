"""
Data Models for structured responses.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class CrowdZone:
    zone_name: str
    occupancy_pct: int
    status_color: str
    wait_mins: int

@dataclass
class TransportRoute:
    service_name: str
    status: str
    delay_mins: int
    crowd_level: str

@dataclass
class Incident:
    time_reported: str
    type: str
    location: str
    status: str
    
@dataclass
class SustainabilityMetrics:
    energy_saved_kwh: int
    plastic_recycled_kg: int
    carbon_offset_tons: float
    water_saved_liters: int
