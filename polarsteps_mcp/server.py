"""
Polarsteps MCP Server

A Model Context Protocol server that provides tools and resources for 
interacting with the Polarsteps API.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ReadResourceRequest,
    ReadResourceResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
    Resource,
    TextContent,
    Tool,
)
from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings

try:
    from polarsteps_api.api.polarsteps import PolarstepsClient
    from polarsteps_api.config import PolarstepsConfig
    from polarsteps_api.models.responses import TripResponse, UserResponse
except ImportError as e:
    logging.error(f"Failed to import polarsteps_api: {e}")
    logging.error("Make sure polarsteps_api is installed or in the Python path")
    sys.exit(1)


class PolarstepsMCPSettings(BaseSettings):
    """Settings for the Polarsteps MCP server"""
    
    model_config = {"env_prefix": "POLARSTEPS_"}
    
    remember_token: Optional[str] = Field(
        default=None,
        description="Polarsteps remember token for authentication"
    )
    base_url: str = Field(
        default="https://www.polarsteps.com",
        description="Base URL for the Polarsteps API"
    )


class PolarstepsMCPServer:
    """MCP server for Polarsteps API"""
    
    def __init__(self, settings: Optional[PolarstepsMCPSettings] = None):
        self.settings = settings or PolarstepsMCPSettings()
        self.server = Server("polarsteps-mcp")
        self._client: Optional[PolarstepsClient] = None
        
        # Register handlers
        self.server.list_tools = self.list_tools
        self.server.call_tool = self.call_tool
        self.server.list_resources = self.list_resources
        self.server.read_resource = self.read_resource
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)
    
    @property
    def client(self) -> PolarstepsClient:
        """Get or create the Polarsteps client"""
        if self._client is None:
            if not self.settings.remember_token:
                raise ValueError(
                    "Remember token is required. Set POLARSTEPS_REMEMBER_TOKEN "
                    "environment variable or pass it during initialization."
                )
            
            config = PolarstepsConfig(
                remember_token=self.settings.remember_token,
                base_url=self.settings.base_url
            )
            self._client = PolarstepsClient(config=config)
        
        return self._client
    
    async def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
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
        try:
            if request.params.name == "get_trip":
                return await self._get_trip(request.params.arguments)
            elif request.params.name == "get_user":
                return await self._get_user(request.params.arguments)
            elif request.params.name == "get_user_trips":
                return await self._get_user_trips(request.params.arguments)
            elif request.params.name == "search_trips":
                return await self._search_trips(request.params.arguments)
            else:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Unknown tool: {request.params.name}"
                        )
                    ],
                    isError=True
                )
        except Exception as e:
            self.logger.error(f"Error calling tool {request.params.name}: {e}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error: {str(e)}"
                    )
                ],
                isError=True
            )
    
    async def _get_trip(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get trip information"""
        trip_id = arguments.get("trip_id")
        if not trip_id:
            return CallToolResult(
                content=[TextContent(type="text", text="trip_id is required")],
                isError=True
            )
        
        try:
            response = self.client.get_trip(str(trip_id))
            
            # Format the response for better readability
            trip_info = {
                "id": response.trip_id,
                "uuid": response.trip_uuid,
                "name": response.trip_name,
                "display_name": response.display_name,
                "slug": response.slug,
                "summary": response.summary,
                "start_date": response.start_date,
                "end_date": response.end_date,
                "total_km": response.total_km,
                "step_count": response.step_count,
                "views": response.views,
                "visibility": response.visibility,
                "timezone_id": response.timezone_id,
                "cover_photo_path": response.cover_photo_path,
                "user_id": response.user_id,
                "user": response.user,
                "steps_count": len(response.all_steps or [])
            }
            
            formatted_text = f"""Trip Information:
- ID: {trip_info['id']}
- Name: {trip_info['name']}
- Display Name: {trip_info['display_name']}
- Summary: {trip_info['summary']}
- Total Distance: {trip_info['total_km']} km
- Steps: {trip_info['step_count']}
- Views: {trip_info['views']}
- Start Date: {trip_info['start_date']}
- End Date: {trip_info['end_date']}
- Timezone: {trip_info['timezone_id']}
- User ID: {trip_info['user_id']}
- Steps Count: {trip_info['steps_count']}"""
            
            return CallToolResult(
                content=[TextContent(type="text", text=formatted_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to get trip: {str(e)}")],
                isError=True
            )
    
    async def _get_user(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get user information"""
        username = arguments.get("username")
        if not username:
            return CallToolResult(
                content=[TextContent(type="text", text="username is required")],
                isError=True
            )
        
        try:
            response = self.client.get_user_by_username(str(username))
            
            user_info = {
                "id": response.user_id,
                "username": response.username,
                "uuid": response.uuid,
                "first_name": response.first_name,
                "last_name": response.last_name,
                "email": response.email,
                "description": response.description,
                "profile_image_path": response.profile_image_path,
                "living_location_name": response.living_location_name,
                "locale": response.locale,
                "visibility": response.visibility,
                "creation_date": response.creation_date,
                "country_count": response.country_count,
                "trips_count": len(response.alltrips or []),
                "followers_count": len(response.followers or []),
                "followees_count": len(response.followees or []),
            }
            
            formatted_text = f"""User Information:
- ID: {user_info['id']}
- Username: {user_info['username']}
- Name: {user_info['first_name']} {user_info['last_name']}
- Email: {user_info['email']}
- Description: {user_info['description']}
- Location: {user_info['living_location_name']}
- Locale: {user_info['locale']}
- Countries Visited: {user_info['country_count']}
- Total Trips: {user_info['trips_count']}
- Followers: {user_info['followers_count']}
- Following: {user_info['followees_count']}
- Creation Date: {user_info['creation_date']}"""
            
            return CallToolResult(
                content=[TextContent(type="text", text=formatted_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to get user: {str(e)}")],
                isError=True
            )
    
    async def _get_user_trips(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get all trips for a user"""
        username = arguments.get("username")
        if not username:
            return CallToolResult(
                content=[TextContent(type="text", text="username is required")],
                isError=True
            )
        
        try:
            response = self.client.get_user_by_username(str(username))
            trips = response.alltrips or []
            
            if not trips:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"No trips found for user {username}")]
                )
            
            formatted_text = f"Trips for user {username}:\n\n"
            for i, trip in enumerate(trips, 1):
                formatted_text += f"{i}. {trip.get('name', 'Unnamed Trip')}\n"
                formatted_text += f"   - ID: {trip.get('id')}\n"
                formatted_text += f"   - Summary: {trip.get('summary', 'No summary')}\n"
                formatted_text += f"   - Distance: {trip.get('total_km', 0)} km\n"
                formatted_text += f"   - Steps: {trip.get('step_count', 0)}\n"
                formatted_text += f"   - Views: {trip.get('views', 0)}\n\n"
            
            return CallToolResult(
                content=[TextContent(type="text", text=formatted_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to get user trips: {str(e)}")],
                isError=True
            )
    
    async def _search_trips(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Search for trips (placeholder implementation)"""
        query = arguments.get("query")
        if not query:
            return CallToolResult(
                content=[TextContent(type="text", text="query is required")],
                isError=True
            )
        
        # This is a placeholder implementation
        # In a real implementation, you would need to add search functionality to the API
        return CallToolResult(
            content=[TextContent(
                type="text", 
                text=f"Search functionality for '{query}' is not yet implemented in the base API. "
                     "You can search for specific users and browse their trips instead."
            )]
        )
    
    async def list_resources(self, request: ListResourcesRequest) -> ListResourcesResult:
        """List available resources"""
        resources = [
            Resource(
                uri=AnyUrl("polarsteps://config"),
                name="Polarsteps Configuration",
                description="Current configuration settings for the Polarsteps MCP server",
                mimeType="application/json"
            ),
            Resource(
                uri=AnyUrl("polarsteps://help"),
                name="Polarsteps Help",
                description="Help documentation for using the Polarsteps MCP server",
                mimeType="text/plain"
            )
        ]
        
        return ListResourcesResult(resources=resources)
    
    async def read_resource(self, request: ReadResourceRequest) -> ReadResourceResult:
        """Get a specific resource"""
        if request.uri == "polarsteps://config":
            config_info = {
                "base_url": self.settings.base_url,
                "has_token": bool(self.settings.remember_token),
                "version": "0.1.0"
            }
            return ReadResourceResult(
                contents=[
                    TextContent(
                        type="text",
                        text=str(config_info)
                    )
                ]
            )
        
        elif request.uri == "polarsteps://help":
            help_text = """Polarsteps MCP Server Help

Available Tools:
1. get_trip(trip_id) - Get detailed trip information
2. get_user(username) - Get user profile and basic info
3. get_user_trips(username) - Get all trips for a user
4. search_trips(query) - Search for trips (placeholder)

Setup:
- Set POLARSTEPS_REMEMBER_TOKEN environment variable
- Optionally set POLARSTEPS_BASE_URL (defaults to https://www.polarsteps.com)

Examples:
- Get trip: get_trip(trip_id="12345")
- Get user: get_user(username="johndoe")
- Get user trips: get_user_trips(username="johndoe")
"""
            return ReadResourceResult(
                contents=[
                    TextContent(
                        type="text",
                        text=help_text
                    )
                ]
            )
        
        else:
            raise ValueError(f"Unknown resource: {request.uri}")
    
    async def run(self, read_stream, write_stream, initialization_options=None):
        """Run the MCP server with the provided streams"""
        try:
            # Test the client connection
            if self.settings.remember_token:
                self.logger.info("Testing Polarsteps API connection...")
                _ = self.client  # This will initialize and test the client
                self.logger.info("Successfully connected to Polarsteps API")
            else:
                self.logger.warning("No remember token provided. Tools will fail until token is set.")
            
            # Run the server with streams
            await self.server.run(read_stream, write_stream, initialization_options or {})
        except Exception as e:
            self.logger.error(f"Failed to run server: {e}")
            raise


async def main():
    """Main entry point for command-line usage"""
    import sys
    from mcp.server.stdio import stdio_server
    
    settings = PolarstepsMCPSettings()
    server = PolarstepsMCPServer(settings)
    
    # Run with stdio streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


def cli_main():
    """Command-line entry point"""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()