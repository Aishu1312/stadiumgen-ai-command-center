import pytest
from models.data_models import CrowdZone, Incident

def test_crowdzone_model():
    """Test CrowdZone data class validation."""
    zone = CrowdZone(zone_name="North Gate", occupancy_pct=85, status_color="red", wait_mins=15)
    assert zone.zone_name == "North Gate"
    assert zone.occupancy_pct == 85

def test_incident_model():
    """Test Incident data class validation."""
    incident = Incident(time_reported="10:00", type="Medical", location="Sector A", status="Open")
    assert incident.type == "Medical"
    assert incident.status == "Open"
