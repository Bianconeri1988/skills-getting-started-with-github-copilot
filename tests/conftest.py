"""Pytest configuration and fixtures for FastAPI tests"""
import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
import sys
from pathlib import Path

# Add src directory to path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities as original_activities


@pytest.fixture
def app_with_reset_state():
    """Provide TestClient with fresh app state for each test (function scope)
    
    Ensures zero state bleed between tests by resetting activities to initial state.
    """
    # Deep copy the original activities to reset state
    app.dependency_overrides = {}
    
    # Create a fresh copy of activities for this test
    fresh_activities = deepcopy(original_activities)
    
    # Replace the app's activities with fresh copy
    import app as app_module
    app_module.activities = fresh_activities
    
    # Create client and yield it
    client = TestClient(app)
    yield client
    
    # Reset app activities back to original after test completes
    app_module.activities = deepcopy(original_activities)


@pytest.fixture
def client(app_with_reset_state):
    """Fixture providing TestClient for API testing"""
    return app_with_reset_state


@pytest.fixture
def valid_email():
    """Common valid email for signup tests"""
    return "testuser@mergington.edu"


@pytest.fixture
def valid_activity_name():
    """Common valid activity name for signup/unregister tests"""
    return "Chess Club"


@pytest.fixture
def invalid_activity_name():
    """Invalid activity name that doesn't exist"""
    return "Nonexistent Activity"


@pytest.fixture
def sample_activities_list():
    """List of all valid activity names available in the API"""
    return list(original_activities.keys())
