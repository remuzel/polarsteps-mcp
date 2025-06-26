from unittest.mock import Mock, patch

import pytest
from mcp.types import TextContent
from polarsteps_api import PolarstepsClient
from polarsteps_api.models import Stats, Trip, User

from polarsteps_mcp.tools import (
    GetTripInput,
    GetUserInput,
    GetUserSocialStatusInput,
    GetUserStatsInput,
    GetUserTripsInput,
    PolarstepsTool,
    get_trip,
    get_user,
    get_user_social_status,
    get_user_stats,
    get_user_trips,
)


@pytest.fixture
def mock_polarsteps_client():
    """Create a mock PolarstepsClient for testing."""
    return Mock(spec=PolarstepsClient)


@pytest.fixture
def sample_user():
    """Create a sample User object for testing."""
    return User(
        id=12345,
        uuid="550e8400-e29b-41d4-a716-446655440000",
        username="testuser",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        description="Travel enthusiast",
        country_count=15,
        stats=Stats(
            continents=[],
            country_codes=[],
            country_count=15,
            furthest_place_from_home_country="",
            furthest_place_from_home_km=0,
            furthest_place_from_home_location="",
            km_count=50000,
            last_trip_end_date=0,
            like_count=0,
            step_count=25,
            time_traveled_in_seconds=0,
            trip_count=10,
            world_percentage=0,
        ),
        followers=[
            User(
                id=1, uuid="550e8400-e29b-41d4-a716-446655440001", username="follower1"
            )
        ],
        followees=[
            User(
                id=2, uuid="550e8400-e29b-41d4-a716-446655440002", username="followee1"
            )
        ],
        follow_requests=[
            User(
                id=3, uuid="550e8400-e29b-41d4-a716-446655440003", username="requester1"
            )
        ],
        sent_follow_requests=[
            User(
                id=4, uuid="550e8400-e29b-41d4-a716-446655440004", username="requested1"
            )
        ],
        alltrips=[
            Trip(
                id=1000001,
                uuid="550e8400-e29b-41d4-a716-446655440001",
                name="Europe Adventure",
                display_name="Europe Adventure 2023",
                start_date=1672531200,  # 2023-01-01
                end_date=1675209600,  # 2023-02-01
                step_count=15,
                total_km=5000.0,
            ),
            Trip(
                id=1000002,
                uuid="550e8400-e29b-41d4-a716-446655440002",
                name="Asia Journey",
                display_name="Asia Journey 2023",
                start_date=1677628800,  # 2023-03-01
                end_date=1680307200,  # 2023-04-01
                step_count=20,
                total_km=8000.0,
            ),
        ],
    )


@pytest.fixture
def sample_trip():
    """Create a sample Trip object for testing."""
    return Trip(
        id=1000001,
        uuid="550e8400-e29b-41d4-a716-446655440001",
        name="Europe Adventure",
        display_name="Europe Adventure 2023",
        summary="An amazing journey through Europe",
        start_date=1672531200,
        end_date=1675209600,
        total_km=5000.0,
        step_count=15,
        all_steps=[
            Mock(location=Mock(name="Paris", country="France")),
            Mock(location=Mock(name="Rome", country="Italy")),
        ],
    )


@pytest.fixture
def not_found_user():
    """Create a User object representing a not found user."""
    return User(id=-1, uuid="00000000-0000-4000-8000-000000000000", username="unknown")


@pytest.fixture
def not_found_trip():
    """Create a Trip object representing a not found trip."""
    return Trip(id=-1, uuid="00000000-0000-4000-8000-000000000000")


class TestGetUser:
    """Test cases for the get_user function."""

    def test_get_user_success(self, mock_polarsteps_client, sample_user):
        """Test successful user retrieval."""
        with patch("polarsteps_mcp.tools._get_user", return_value=sample_user):
            input_data = GetUserInput(username="testuser")
            result = get_user(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "John Doe" in result[0].text

    def test_get_user_not_found(self, mock_polarsteps_client, not_found_user):
        """Test user not found scenario."""
        with patch("polarsteps_mcp.tools._get_user", return_value=not_found_user):
            input_data = GetUserInput(username="nonexistent")
            result = get_user(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Could not find user with username: nonexistent" in result[0].text

    @pytest.mark.parametrize(
        "username",
        ["validuser", "user_with_underscore", "user123", "a" * 50],  # long username
    )
    def test_get_user_input_validation(self, username):
        """Test GetUserInput validation with various usernames."""
        input_data = GetUserInput(username=username)
        assert input_data.username == username


class TestGetUserStats:
    """Test cases for the get_user_stats function."""

    def test_get_user_stats_success(self, mock_polarsteps_client, sample_user):
        """Test successful user stats retrieval."""
        with patch("polarsteps_mcp.tools._get_user", return_value=sample_user):
            input_data = GetUserStatsInput(username="testuser")
            result = get_user_stats(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            # Should contain JSON representation of stats
            assert "country_count" in result[0].text or "km_count" in result[0].text

    def test_get_user_stats_no_stats(self, mock_polarsteps_client):
        """Test user with no stats."""
        user_without_stats = User(
            id=12345,
            uuid="550e8400-e29b-41d4-a716-446655440000",
            username="testuser",
            stats=None,
        )

        with patch("polarsteps_mcp.tools._get_user", return_value=user_without_stats):
            input_data = GetUserStatsInput(username="testuser")
            result = get_user_stats(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert "Could not find user with username: testuser" in result[0].text


class TestGetUserTrips:
    """Test cases for the get_user_trips function."""

    def test_get_user_trips_success(self, mock_polarsteps_client, sample_user):
        """Test successful user trips retrieval."""
        with patch("polarsteps_mcp.tools._get_user", return_value=sample_user):
            input_data = GetUserTripsInput(username="testuser", max_trips=10)
            result = get_user_trips(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Europe Adventure" in result[0].text
            assert "Asia Journey" in result[0].text
            assert "Top 10 trips:" in result[0].text

    def test_get_user_trips_limit_trips(self, mock_polarsteps_client, sample_user):
        """Test limiting the number of trips returned."""
        with patch("polarsteps_mcp.tools._get_user", return_value=sample_user):
            input_data = GetUserTripsInput(username="testuser", max_trips=1)
            result = get_user_trips(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert "Top 1 trips:" in result[0].text
            # Should only contain the first trip
            assert "Europe Adventure" in result[0].text
            assert "Asia Journey" not in result[0].text

    def test_get_user_trips_no_trips(self, mock_polarsteps_client):
        """Test user with no trips."""
        user_without_trips = User(
            id=12345,
            uuid="550e8400-e29b-41d4-a716-446655440000",
            username="testuser",
            alltrips=None,
        )

        with patch("polarsteps_mcp.tools._get_user", return_value=user_without_trips):
            input_data = GetUserTripsInput(username="testuser")  # type: ignore
            result = get_user_trips(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert "Could not find user with username: testuser" in result[0].text

    @pytest.mark.parametrize("max_trips", [1, 5, 10, 50, 100])
    def test_get_user_trips_max_trips_validation(self, max_trips):
        """Test GetUserTripsInput validation with various max_trips values."""
        input_data = GetUserTripsInput(username="testuser", max_trips=max_trips)
        assert input_data.max_trips == max_trips


class TestGetUserSocialStatus:
    """Test cases for the get_user_social_status function."""

    def test_get_user_social_status_success(self, mock_polarsteps_client, sample_user):
        """Test successful user social status retrieval."""
        with patch("polarsteps_mcp.tools._get_user", return_value=sample_user):
            input_data = GetUserSocialStatusInput(username="testuser")
            result = get_user_social_status(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "John Doe" in result[0].text
            assert "follows" in result[0].text
            assert "followed by" in result[0].text

    def test_get_user_social_status_incomplete_profile(self, mock_polarsteps_client):
        """Test user with incomplete social profile."""
        user_incomplete = User(
            id=12345,
            uuid="550e8400-e29b-41d4-a716-446655440000",
            username="testuser",
            first_name="John",
            last_name="Doe",
            followers=None,
            followees=None,
        )

        with patch("polarsteps_mcp.tools._get_user", return_value=user_incomplete):
            input_data = GetUserSocialStatusInput(username="testuser")
            result = get_user_social_status(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert "incomplete social profile" in result[0].text


class TestGetTrip:
    """Test cases for the get_trip function."""

    def test_get_trip_success(self, mock_polarsteps_client):
        """Test successful trip retrieval."""
        # Create a trip with proper step structure - we'll mock the _get_trip function instead
        sample_trip = Trip(
            id=1000001,
            uuid="550e8400-e29b-41d4-a716-446655440001",
            name="Europe Adventure",
            display_name="Europe Adventure 2023",
            summary="An amazing journey through Europe",
            start_date=1672531200,
            end_date=1675209600,
            total_km=5000.0,
            step_count=15,
            all_steps=[],  # Empty steps to avoid validation issues
        )

        # Mock the all_steps attribute to have the location data we need
        mock_step1 = Mock()
        mock_step1.location.name = "Paris"
        mock_step1.location.country = "France"

        mock_step2 = Mock()
        mock_step2.location.name = "Rome"
        mock_step2.location.country = "Italy"

        sample_trip.all_steps = [mock_step1, mock_step2]

        with patch("polarsteps_mcp.tools._get_trip", return_value=sample_trip):
            input_data = GetTripInput(trip_id=1000001)
            result = get_trip(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Europe Adventure" in result[0].text
            assert "Paris (France)" in result[0].text
            assert "Rome (Italy)" in result[0].text
            assert "An amazing journey through Europe" in result[0].text

    def test_get_trip_no_steps(self, mock_polarsteps_client):
        """Test trip with no steps."""
        trip_no_steps = Trip(
            id=1000001,
            uuid="550e8400-e29b-41d4-a716-446655440001",
            name="Simple Trip",
            total_km=1000.0,
            summary="A simple trip",
            all_steps=[],
        )

        with patch("polarsteps_mcp.tools._get_trip", return_value=trip_no_steps):
            input_data = GetTripInput(trip_id=1000001)
            result = get_trip(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert "Simple Trip" in result[0].text
            assert "0 days long trip" in result[0].text

    def test_get_trip_not_found(self, mock_polarsteps_client, not_found_trip):
        """Test trip not found scenario."""
        with patch("polarsteps_mcp.tools._get_trip", return_value=not_found_trip):
            input_data = GetTripInput(trip_id=1000001)
            result = get_trip(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert "Could not find trip with ID: 1000001" in result[0].text

    @pytest.mark.parametrize("trip_id", [1000000, 1234567, 9999999])
    def test_get_trip_input_validation_valid(self, trip_id):
        """Test GetTripInput validation with valid trip IDs."""
        input_data = GetTripInput(trip_id=trip_id)
        assert input_data.trip_id == trip_id

    @pytest.mark.parametrize("trip_id", [0, 999999, -1])
    def test_get_trip_input_validation_invalid(self, trip_id):
        """Test GetTripInput validation with invalid trip IDs."""
        with pytest.raises(ValueError):
            GetTripInput(trip_id=trip_id)


class TestPolarstepsTool:
    """Test that all tools are correctly defined."""

    @pytest.mark.parametrize("tool", list(PolarstepsTool))
    def test_valid_tool_definition(self, tool):
        # Validate value
        assert tool.value is not None
        assert isinstance(tool.value, str)
        assert len(tool.value) > 0
        # Validate description
        assert tool.description is not None
        assert isinstance(tool.description, str)
        assert len(tool.description) > 0
        # Validate schema
        schema = tool.schema
        assert "type" in schema
        assert "properties" in schema
        assert isinstance(schema["properties"], dict)
