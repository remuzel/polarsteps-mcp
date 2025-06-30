from unittest.mock import Mock, patch

import pytest
from mcp.types import TextContent
from polarsteps_api import PolarstepsClient
from polarsteps_api.models import Location, Stats, Step, Trip, User

from polarsteps_mcp.tools import (
    GetTravelStats,
    GetTripInput,
    GetTripsByNameInput,
    GetTripsInput,
    GetUserInput,
    PolarstepsTool,
    get_travel_stats,
    get_trip,
    get_trips,
    get_trips_by_name,
    get_user,
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
                name="Europe Adventure 2023",
                start_date=1672531200,  # 2023-01-01
                end_date=1675209600,  # 2023-02-01
                step_count=15,
                total_km=5000.0,
            ),
            Trip(
                id=1000002,
                uuid="550e8400-e29b-41d4-a716-446655440002",
                name="Asia Journey 2023",
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
        name="Europe Adventure 2023",
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
            # The result should be JSON string containing user summary
            import json
            user_data = json.loads(result[0].text)
            assert user_data["first_name"] == "John"
            assert user_data["last_name"] == "Doe"
            assert user_data["username"] == "testuser"

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
            input_data = GetTravelStats(username="testuser")
            result = get_travel_stats(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            # Should contain JSON representation of stats
            import json
            stats_data = json.loads(result[0].text)
            assert stats_data["country_count"] == 15
            assert stats_data["km_count"] == 50000

    def test_get_user_stats_no_stats(self, mock_polarsteps_client):
        """Test user with no stats."""
        user_without_stats = User(
            id=12345,
            uuid="550e8400-e29b-41d4-a716-446655440000",
            username="testuser",
            stats=None,
        )

        with patch("polarsteps_mcp.tools._get_user", return_value=user_without_stats):
            input_data = GetTravelStats(username="testuser")
            result = get_travel_stats(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert "User @testuser does not have travel stats" in result[0].text


class TestGetUserTrips:
    """Test cases for the get_user_trips function."""

    def test_get_user_trips_success(self, mock_polarsteps_client, sample_user):
        """Test successful user trips retrieval."""
        with patch("polarsteps_mcp.tools._get_user", return_value=sample_user):
            input_data = GetTripsInput(username="testuser", n_trips=10)
            result = get_trips(mock_polarsteps_client, input_data)

            # Should return a list with one TextContent per trip
            assert len(result) == 2  # sample_user has 2 trips
            assert all(isinstance(item, TextContent) for item in result)

            # Check that each result contains JSON data for a trip
            import json
            trip1_data = json.loads(result[0].text)
            trip2_data = json.loads(result[1].text)

            assert trip1_data["name"] == "Europe Adventure 2023"
            assert trip2_data["name"] == "Asia Journey 2023"

    def test_get_user_trips_limit_trips(self, mock_polarsteps_client, sample_user):
        """Test limiting the number of trips returned."""
        with patch("polarsteps_mcp.tools._get_user", return_value=sample_user):
            input_data = GetTripsInput(username="testuser", n_trips=1)
            result = get_trips(mock_polarsteps_client, input_data)

            # Should return only 1 trip due to max_trips=1
            assert len(result) == 1

            # Check first trip
            import json
            trip1_data = json.loads(result[0].text)
            assert trip1_data["name"] == "Europe Adventure 2023"

    def test_get_user_trips_max_trips_larger_than_available(self, mock_polarsteps_client, sample_user):
        """Test max_trips parameter when larger than available trips."""
        with patch("polarsteps_mcp.tools._get_user", return_value=sample_user):
            input_data = GetTripsInput(username="testuser", n_trips=10)
            result = get_trips(mock_polarsteps_client, input_data)

            # Should return all available trips (2) even though max_trips=10
            assert len(result) == 2

            import json
            trip1_data = json.loads(result[0].text)
            trip2_data = json.loads(result[1].text)
            assert trip1_data["name"] == "Europe Adventure 2023"
            assert trip2_data["name"] == "Asia Journey 2023"

    def test_get_user_trips_no_trips(self, mock_polarsteps_client):
        """Test user with no trips."""
        user_without_trips = User(
            id=12345,
            uuid="550e8400-e29b-41d4-a716-446655440000",
            username="testuser",
            alltrips=None,
        )

        with patch("polarsteps_mcp.tools._get_user", return_value=user_without_trips):
            input_data = GetTripsInput(username="testuser")  # type: ignore
            result = get_trips(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert "User @testuser does not have any trips!" in result[0].text

    @pytest.mark.parametrize("max_trips", [1, 5, 10, 50, 100])
    def test_get_user_trips_max_trips_validation(self, max_trips):
        """Test GetUserTripsInput validation with various max_trips values."""
        input_data = GetTripsInput(username="testuser", n_trips=max_trips)
        assert input_data.n_trips == max_trips


class TestGetTrip:
    """Test cases for the get_trip function."""

    def test_get_trip_success(self, mock_polarsteps_client):
        """Test successful trip retrieval."""
        # Create a trip with proper step structure - we'll mock the _get_trip function instead
        sample_trip = Trip(
            id=1000001,
            uuid="550e8400-e29b-41d4-a716-446655440001",
            name="Europe Adventure 2023",
            summary="An amazing journey through Europe",
            start_date=1672531200,
            end_date=1675209600,
            total_km=5000.0,
            step_count=15,
            all_steps=[],  # Empty steps to avoid validation issues
        )

        # Mock the all_steps attribute to have the location data we need
        mock_step1 = Mock()
        mock_step1.name = "Paris Visit"  # Add name attribute
        mock_step1.location.name = "Paris"
        mock_step1.location.country = "France"
        mock_step1.description = "Beautiful city"
        mock_step1.is_deleted = False
        mock_step1.start_time = 1672531200
        mock_step1.media = []  # Add empty media list
        mock_step1.to_summary.return_value = {
            "name": "Paris Visit",
            "location": {"name": "Paris", "country": "France"},
            "description": "Beautiful city",
            "start_time": 1672531200
        }

        mock_step2 = Mock()
        mock_step2.name = "Rome Visit"  # Add name attribute
        mock_step2.location.name = "Rome"
        mock_step2.location.country = "Italy"
        mock_step2.description = "Historic city"
        mock_step2.is_deleted = False
        mock_step2.start_time = 1672617600
        mock_step2.media = []  # Add empty media list
        mock_step2.to_summary.return_value = {
            "name": "Rome Visit",
            "location": {"name": "Rome", "country": "Italy"},
            "description": "Historic city",
            "start_time": 1672617600
        }

        sample_trip.all_steps = [mock_step1, mock_step2]

        with patch("polarsteps_mcp.tools._get_trip", return_value=sample_trip):
            input_data = GetTripInput(trip_id=1000001) # type: ignore
            result = get_trip(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert isinstance(result[0], TextContent)

            # The result should be JSON string containing trip detailed summary
            import json
            trip_data = json.loads(result[0].text)
            assert trip_data["name"] == "Europe Adventure 2023"
            assert trip_data["summary"] == "An amazing journey through Europe"
            assert trip_data["total_km"] == 5000.0
            assert "steps" in trip_data

    def test_get_trip_no_steps(self, mock_polarsteps_client):
        """Test trip with no steps."""
        trip_no_steps = Trip(
            id=1000001,
            uuid="550e8400-e29b-41d4-a716-446655440001",
            name="Simple Trip",
            total_km=1000.0,
            summary="A simple trip",
            start_date=1672531200,
            end_date=1672531200,  # Same day trip
            all_steps=[],
        )

        with patch("polarsteps_mcp.tools._get_trip", return_value=trip_no_steps):
            input_data = GetTripInput(trip_id=1000001) # type: ignore
            result = get_trip(mock_polarsteps_client, input_data)

            assert len(result) == 1

            # The result should be JSON string containing trip detailed summary
            import json
            trip_data = json.loads(result[0].text)
            assert trip_data["name"] == "Simple Trip"
            assert trip_data["summary"] == "A simple trip"
            assert trip_data["total_km"] == 1000.0
            assert trip_data["steps"] == []  # No steps with descriptions

    def test_get_trip_fewer_steps(self, mock_polarsteps_client):
        """Test trip with one step but requesting more."""
        trip_one_step = Trip(
            id=1000001,
            uuid="550e8400-e29b-41d4-a716-446655440001",
            name="Simple Trip",
            total_km=1000.0,
            summary="A simple trip",
            start_date=1672531200,
            end_date=1672531200,
            all_steps=[Step(
                id=1001,
                uuid='123',
                trip_id=1000001,
                name="Sample Step",
                description="A nice place",  # Has description so will be included
                location=Location(name="Fairy Land", country="Fairy Land"),
                start_time=1672531200,
                is_deleted=False,
            )],
        )

        with patch("polarsteps_mcp.tools._get_trip", return_value=trip_one_step):
            input_data = GetTripInput(trip_id=1000001, n_steps=2)
            result = get_trip(mock_polarsteps_client, input_data)

            assert len(result) == 1

            # The result should be JSON string containing trip detailed summary
            import json
            trip_data = json.loads(result[0].text)
            assert trip_data["name"] == "Simple Trip"
            assert len(trip_data["steps"]) == 1
            assert trip_data["steps"][0]["name"] == "Sample Step"
            assert trip_data["steps"][0]["location"]["country"] == "Fairy Land"

    def test_get_trip_not_found(self, mock_polarsteps_client, not_found_trip):
        """Test trip not found scenario."""
        with patch("polarsteps_mcp.tools._get_trip", return_value=not_found_trip):
            input_data = GetTripInput(trip_id=1000001) # type: ignore
            result = get_trip(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert "Could not find trip with ID: 1000001" in result[0].text

    @pytest.mark.parametrize("trip_id", [1000000, 1234567, 9999999])
    def test_get_trip_input_validation_valid(self, trip_id):
        """Test GetTripInput validation with valid trip IDs."""
        input_data = GetTripInput(trip_id=trip_id) # type: ignore
        assert input_data.trip_id == trip_id

    @pytest.mark.parametrize("trip_id", [0, 999999, -1])
    def test_get_trip_input_validation_invalid(self, trip_id):
        """Test GetTripInput validation with invalid trip IDs."""
        with pytest.raises(ValueError):
            GetTripInput(trip_id=trip_id) # type: ignore

class TestGetTripsByName:
    """Test cases for get_trips_by_name."""

    def test_get_trips_by_name_no_results(self, mock_polarsteps_client, sample_user):
        """Test no matching trips found."""
        with patch("polarsteps_mcp.tools._get_user", return_value=sample_user):
            input_data = GetTripsByNameInput(username="testuser", name_query="doesn't-exist")
            result = get_trips_by_name(mock_polarsteps_client, input_data)

            assert result == []

    def test_get_trips_by_name(self, mock_polarsteps_client, sample_user):
        """Test successful search for trips by name."""
        with patch("polarsteps_mcp.tools._get_user", return_value=sample_user):
            input_data = GetTripsByNameInput(username="testuser", name_query="Europe")
            result = get_trips_by_name(mock_polarsteps_client, input_data)

            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == '{"id":1000001,"name":"Europe Adventure 2023"}'

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
