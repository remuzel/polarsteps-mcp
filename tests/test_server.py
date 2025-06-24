import pytest
from polarsteps_api import PolarstepsClient
from polarsteps_mcp.server import get_trip, get_user


@pytest.fixture
def polarsteps_client() -> PolarstepsClient:
    return PolarstepsClient()


def test_get_user_with_valid_id(polarsteps_client):
    user_data = get_user(polarsteps_client, "remuzel")
    assert user_data.id is not None
    assert len(user_data.alltrips or []) > 0


def test_get_user_with_invalid_id(polarsteps_client):
    user_data = get_user(polarsteps_client, "invalid-user")
    assert user_data.id == -1
    assert user_data.uuid == "00000000-0000-4000-8000-000000000000"
    assert user_data.username == "unknown"


def test_get_trip_with_valid_id(polarsteps_client):
    trip_data = get_trip(polarsteps_client, 18289661)
    assert trip_data.id == 18289661
    assert len(trip_data.all_steps or []) > 0


def test_get_trip_with_invalid_id(polarsteps_client):
    trip_data = get_trip(polarsteps_client, 1)
    assert trip_data.id == -1
    assert trip_data.uuid == "00000000-0000-4000-8000-000000000000"
