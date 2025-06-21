"""
Test configuration for Polarsteps MCP Server tests
"""

import pytest
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the polarsteps_api
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "polarsteps_api"))


@pytest.fixture
def mock_polarsteps_response():
    """Mock response data for testing"""
    return {
        "trip": {
            "id": 12345,
            "uuid": "test-uuid",
            "name": "Test Trip",
            "display_name": "Test Display Name",
            "summary": "A test trip for unit testing",
            "total_km": 150.5,
            "step_count": 25,
            "views": 100,
            "start_date": 1640995200.0,
            "end_date": 1641081600.0,
            "timezone_id": "UTC",
            "user_id": 123,
            "all_steps": []
        },
        "user": {
            "id": 123,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "description": "Test user for unit testing",
            "living_location_name": "Test City",
            "locale": "en",
            "country_count": 8,
            "alltrips": [],
            "followers": [],
            "followees": [],
            "creation_date": 1640995200.0
        }
    }