import pytest
from utils.performance import track_time

def test_track_time_decorator():
    """Test that the performance tracker decorator does not interfere with the function return."""
    @track_time
    def dummy_func():
        return "success"
        
    assert dummy_func() == "success"
