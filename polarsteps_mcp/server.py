"""
Polarsteps MCP Server

A Model Context Protocol server that provides tools and resources for
interacting with the Polarsteps API.
"""

from typing import Any, Dict

from mcp.server import Server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsResult,
    ReadResourceRequest,
    ReadResourceResult,
    Resource,
    TextContent,
    Tool,
)
from polarsteps_api.api.polarsteps import PolarstepsClient
from polarsteps_api.config import PolarstepsConfig
from pydantic import AnyUrl


class PolarstepsMCPServer:
    """MCP server for Polarsteps API"""

    def __init__(self):
        self.server = Server("polarsteps-mcp")
        self.client = PolarstepsClient(config=PolarstepsConfig())

        # Register handlers
        self.server.list_tools = self.list_tools
        self.server.call_tool = self.call_tool
        self.server.list_resources = self.list_resources
        self.server.read_resource = self.read_resource

    async def list_tools(self) -> ListToolsResult:
        """List available tools"""
        tools = [
            Tool(
                name="get_trip",
                description="Get detailed information about a Polarsteps trip by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "trip_id": {
                            "type": "string",
                            "description": "The ID of the trip to retrieve"
                        }
                    },
                    "required": ["trip_id"]
                }
            ),
            Tool(
                name="get_user",
                description="Get detailed information about a Polarsteps user by username",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "The username of the user to retrieve"
                        }
                    },
                    "required": ["username"]
                }
            ),
            Tool(
                name="get_user_trips",
                description="Get all trips for a specific user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "The username of the user whose trips to retrieve"
                        }
                    },
                    "required": ["username"]
                }
            ),
            Tool(
                name="search_trips",
                description="Search for trips based on criteria",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for trip names or descriptions"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "Optional: Filter trips by user ID"
                        }
                    },
                    "required": ["query"]
                }
            )
        ]

        return ListToolsResult(tools=tools)

    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool calls"""
        name = request.params.name
        args = request.params.arguments or {}

        handlers = {
            "get_trip": self._get_trip,
            "get_user": self._get_user,
            "get_user_trips": self._get_user_trips,
            "search_trips": self._search_trips
        }

        handler = handlers.get(name)
        if not handler:
            return self._error(f"Unknown tool: {name}")

        try:
            return await handler(args)
        except Exception as e:
            return self._error(f"Error: {str(e)}")

    async def _get_trip(self, args: Dict[str, Any]) -> CallToolResult:
        """Get trip information"""
        trip_id = args.get("trip_id")
        if not trip_id:
            return self._error("trip_id is required")

        response = self.client.get_trip(str(trip_id))
        if response.is_error or not response.trip:
            return self._error("Trip not found")

        trip = response.trip
        text = f"""Trip: {trip.name}
ID: {trip.id}
Summary: {trip.summary}
Distance: {trip.total_km} km
Steps: {trip.step_count}
Views: {trip.views}
Dates: {trip.start_date} to {trip.end_date}"""

        return self._success(text)

    async def _get_user(self, args: Dict[str, Any]) -> CallToolResult:
        """Get user information"""
        username = args.get("username")
        if not username:
            return self._error("username is required")

        response = self.client.get_user_by_username(str(username))
        if response.is_error or not response.user:
            return self._error("User not found")

        user = response.user
        trips_count = len(user.alltrips or [])
        followers_count = len(user.followers or [])

        text = f"""User: {user.username}
Name: {user.first_name} {user.last_name}
Location: {user.living_location_name}
Countries: {user.country_count}
Trips: {trips_count}
Followers: {followers_count}"""

        return self._success(text)

    async def _get_user_trips(self, args: Dict[str, Any]) -> CallToolResult:
        """Get all trips for a user"""
        username = args.get("username")
        if not username:
            return self._error("username is required")

        response = self.client.get_user_by_username(str(username))
        if response.is_error or not response.user:
            return self._error("User not found")

        trips = response.user.alltrips or []
        if not trips:
            return self._success(f"No trips found for {username}")

        text = f"Trips for {username}:\n"
        for i, trip in enumerate(trips, 1):
            name = trip.name or "Unnamed Trip"
            text += f"{i}. {name} ({trip.total_km or 0} km, {trip.step_count or 0} steps)\n"

        return self._success(text)

    async def _search_trips(self, args: Dict[str, Any]) -> CallToolResult:
        """Search for trips (placeholder implementation)"""
        query = args.get("query")
        if not query:
            return self._error("query is required")

        return self._success(f"Search for '{query}' not implemented. Use get_user_trips instead.")

    async def list_resources(self, request: ListResourcesRequest) -> ListResourcesResult:
        """List available resources"""
        return ListResourcesResult(resources=[
            Resource(
                uri=AnyUrl("polarsteps://help"),
                name="Polarsteps Help",
                description="Help documentation",
                mimeType="text/plain"
            )
        ])

    async def read_resource(self, request: ReadResourceRequest) -> ReadResourceResult:
        """Get a specific resource"""
        if request.method == "polarsteps://help":
            text = """Tools: get_trip, get_user, get_user_trips, search_trips
Setup: Set POLARSTEPS_REMEMBER_TOKEN env var"""
            return ReadResourceResult(contents=[TextContent(type="text", text=text)])

        raise ValueError(f"Unknown resource: {request.method}")

    def _success(self, text: str) -> CallToolResult:
        """Create success response"""
        return CallToolResult(content=[TextContent(type="text", text=text)])

    def _error(self, text: str) -> CallToolResult:
        """Create error response"""
        return CallToolResult(content=[TextContent(type="text", text=text)], isError=True)

    async def run(self, read_stream, write_stream, initialization_options=None):
        """Run the MCP server with the provided streams"""
        await self.server.run(read_stream, write_stream, initialization_options)


async def main():
    """Main entry point for command-line usage"""
    from mcp.server.stdio import stdio_server

    server = PolarstepsMCPServer()

    # Run with stdio streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


def cli_main():
    """Command-line entry point"""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
