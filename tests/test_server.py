"""
Tests for the Polarsteps MCP Server
"""

from unittest.mock import Mock, patch

import pytest
from mcp.types import (
    CallToolRequest,
    CallToolRequestParams,
    ListResourcesRequest,
    ListToolsRequest,
)

from polarsteps_mcp.server import PolarstepsMCPServer, PolarstepsMCPSettings


class TestPolarstepsMCPServer:
    """Test the MCP server functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.settings = PolarstepsMCPSettings(
            remember_token="test_token",
            base_url="https://test.polarsteps.com"
        )
        self.server = PolarstepsMCPServer(self.settings)

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing available tools"""
        request = ListToolsRequest(method="tools/list", params={})
        result = await self.server.list_tools(request)

        assert len(result.tools) == 4
        tool_names = [tool.name for tool in result.tools]
        assert "get_trip" in tool_names
        assert "get_user" in tool_names
        assert "get_user_trips" in tool_names
        assert "search_trips" in tool_names

    @pytest.mark.asyncio
    async def test_list_resources(self):
        """Test listing available resources"""
        request = ListResourcesRequest(method="resources/list", params={})
        result = await self.server.list_resources(request)

        assert len(result.resources) == 2
        resource_uris = [str(resource.uri) for resource in result.resources]
        assert "polarsteps://config" in resource_uris
        assert "polarsteps://help" in resource_uris

    @pytest.mark.asyncio
    async def test_get_trip_missing_arguments(self):
        """Test get_trip with missing arguments"""
        request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(name="get_trip", arguments={})
        )

        result = await self.server.call_tool(request)
        assert result.isError is True
        assert "trip_id is required" in result.content[0].text

    @pytest.mark.asyncio
    async def test_get_user_missing_arguments(self):
        """Test get_user with missing arguments"""
        request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(name="get_user", arguments={})
        )

        result = await self.server.call_tool(request)
        assert result.isError is True
        assert "username is required" in result.content[0].text

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test calling an unknown tool"""
        request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(name="unknown_tool", arguments={})
        )

        result = await self.server.call_tool(request)
        assert result.isError is True
        assert "Unknown tool: unknown_tool" in result.content[0].text

    @patch('polarsteps_mcp.server.PolarstepsClient')
    @pytest.mark.asyncio
    async def test_get_trip_success(self, mock_client_class):
        """Test successful trip retrieval"""
        # Mock the client and response
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_response = Mock()
        mock_response.trip_id = 12345
        mock_response.trip_name = "Test Trip"
        mock_response.display_name = "Test Display Name"
        mock_response.summary = "Test Summary"
        mock_response.total_km = 100.5
        mock_response.step_count = 10
        mock_response.views = 50
        mock_response.start_date = 1640995200.0
        mock_response.end_date = 1641081600.0
        mock_response.timezone_id = "UTC"
        mock_response.user_id = 123
        mock_response.all_steps = []

        mock_client.get_trip.return_value = mock_response

        # Override the client property
        self.server._client = mock_client

        request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(name="get_trip", arguments={"trip_id": "12345"})
        )

        result = await self.server.call_tool(request)

        assert result.isError is not True
        assert "Test Trip" in result.content[0].text
        assert "100.5 km" in result.content[0].text
        mock_client.get_trip.assert_called_once_with("12345")

    @patch('polarsteps_mcp.server.PolarstepsClient')
    @pytest.mark.asyncio
    async def test_get_user_success(self, mock_client_class):
        """Test successful user retrieval"""
        # Mock the client and response
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_response = Mock()
        mock_response.user_id = 123
        mock_response.username = "testuser"
        mock_response.first_name = "Test"
        mock_response.last_name = "User"
        mock_response.email = "test@example.com"
        mock_response.description = "Test Description"
        mock_response.living_location_name = "Test City"
        mock_response.locale = "en"
        mock_response.country_count = 5
        mock_response.alltrips = []
        mock_response.followers = []
        mock_response.followees = []
        mock_response.creation_date = 1640995200.0

        mock_client.get_user_by_username.return_value = mock_response

        # Override the client property
        self.server._client = mock_client

        request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(name="get_user", arguments={"username": "testuser"})
        )

        result = await self.server.call_tool(request)

        assert result.isError is not True
        assert "testuser" in result.content[0].text
        assert "Test User" in result.content[0].text
        mock_client.get_user_by_username.assert_called_once_with("testuser")


class TestPolarstepsMCPSettings:
    """Test the settings configuration"""

    def test_default_settings(self):
        """Test default configuration values"""
        settings = PolarstepsMCPSettings()
        assert settings.remember_token is None
        assert settings.base_url == "https://www.polarsteps.com"

    def test_custom_settings(self):
        """Test custom configuration values"""
        settings = PolarstepsMCPSettings(
            remember_token="custom_token",
            base_url="https://custom.url"
        )
        assert settings.remember_token == "custom_token"
        assert settings.base_url == "https://custom.url"
