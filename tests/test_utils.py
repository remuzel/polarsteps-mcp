from unittest.mock import Mock

import pydantic_core
import pytest
from mcp.types import TextContent
from polarsteps_api import PolarstepsClient
from polarsteps_api.models import Trip, User

from polarsteps_mcp.utils import _get_trip, _get_user, single_text_content


class TestSingleTextContent:
    """Test cases for the single_text_content utility function."""

    @pytest.mark.parametrize("text", ["", "Test Message", "Multi\nLine"])
    def test_valid_text(self, text):
        # Act
        result = single_text_content(text)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].type == "text"
        assert result[0].text == text

    def test_none_text(self):
        # Act & Assert
        with pytest.raises(pydantic_core._pydantic_core.ValidationError):
            single_text_content(None)  # type: ignore


class TestGetUser:
    """Test cases for the _get_user utility function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock PolarstepsClient."""
        return Mock(spec=PolarstepsClient)

    @pytest.fixture
    def sample_user(self):
        """Create a sample User object."""
        return User(
            id=12345,
            uuid="550e8400-e29b-41d4-a716-446655440000",
            username="testuser",
            first_name="John",
            last_name="Doe",
        )

    def test_get_user_success(self, mock_client, sample_user):
        """Test successful user retrieval."""
        # Arrange
        mock_response = Mock()
        mock_response.is_error = False
        mock_response.user = sample_user
        mock_client.get_user_by_username.return_value = mock_response

        # Act
        result = _get_user(mock_client, "testuser")

        # Assert
        assert result == sample_user
        mock_client.get_user_by_username.assert_called_once_with("testuser")

    def test_get_user_api_error(self, mock_client):
        """Test user retrieval when API returns error."""
        # Arrange
        mock_response = Mock()
        mock_response.is_error = True
        mock_response.user = None
        mock_client.get_user_by_username.return_value = mock_response

        # Act
        result = _get_user(mock_client, "nonexistent")

        # Assert
        assert result.id == -1
        assert result.uuid == "00000000-0000-4000-8000-000000000000"
        assert result.username == "unknown"
        mock_client.get_user_by_username.assert_called_once_with("nonexistent")

    def test_get_user_no_user_in_response(self, mock_client):
        """Test user retrieval when API response has no user."""
        # Arrange
        mock_response = Mock()
        mock_response.is_error = False
        mock_response.user = None
        mock_client.get_user_by_username.return_value = mock_response

        # Act
        result = _get_user(mock_client, "testuser")

        # Assert
        assert result.id == -1
        assert result.uuid == "00000000-0000-4000-8000-000000000000"
        assert result.username == "unknown"


class TestGetTrip:
    """Test cases for the _get_trip utility function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock PolarstepsClient."""
        return Mock(spec=PolarstepsClient)

    @pytest.fixture
    def sample_trip(self):
        """Create a sample Trip object."""
        return Trip(
            id=1000001,
            uuid="550e8400-e29b-41d4-a716-446655440001",
            name="Europe Adventure",
            display_name="Europe Adventure 2023",
        )

    def test_get_trip_success(self, mock_client, sample_trip):
        """Test successful trip retrieval."""
        # Arrange
        mock_response = Mock()
        mock_response.is_error = False
        mock_response.trip = sample_trip
        mock_client.get_trip.return_value = mock_response

        # Act
        result = _get_trip(mock_client, 1000001)

        # Assert
        assert result == sample_trip
        mock_client.get_trip.assert_called_once_with("1000001")

    def test_get_trip_api_error(self, mock_client):
        """Test trip retrieval when API returns error."""
        # Arrange
        mock_response = Mock()
        mock_response.is_error = True
        mock_response.trip = None
        mock_client.get_trip.return_value = mock_response

        # Act
        result = _get_trip(mock_client, 999999)

        # Assert
        assert result.id == -1
        assert result.uuid == "00000000-0000-4000-8000-000000000000"
        mock_client.get_trip.assert_called_once_with("999999")

    def test_get_trip_no_trip_in_response(self, mock_client):
        """Test trip retrieval when API response has no trip."""
        # Arrange
        mock_response = Mock()
        mock_response.is_error = False
        mock_response.trip = None
        mock_client.get_trip.return_value = mock_response

        # Act
        result = _get_trip(mock_client, 1000001)

        # Assert
        assert result.id == -1
        assert result.uuid == "00000000-0000-4000-8000-000000000000"

    def test_get_trip_converts_int_to_string(self, mock_client, sample_trip):
        """Test that trip ID is converted to string for API call."""
        # Arrange
        mock_response = Mock()
        mock_response.is_error = False
        mock_response.trip = sample_trip
        mock_client.get_trip.return_value = mock_response

        # Act
        _get_trip(mock_client, 1234567)

        # Assert
        mock_client.get_trip.assert_called_once_with("1234567")
