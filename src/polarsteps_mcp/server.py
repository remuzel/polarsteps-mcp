from datetime import datetime
from enum import Enum
from typing import Any, Type

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from polarsteps_api import PolarstepsClient
from polarsteps_api.models import Trip, User
from pydantic import BaseModel, Field


# For each tool you're going to use, define the interaction model (what parameters are required, their description, ...)
class GetUser(BaseModel):
    username: str = Field(..., description="The users' username in Polarsteps")


class GetUserStats(BaseModel):
    username: str = Field(..., description="The users' username in Polarsteps")


class GetUserTrips(BaseModel):
    username: str = Field(..., description="The users' username in Polarsteps")
    max_trips: int = Field(
        50, description="The maximum number of trips to return", ge=1_000_000
    )


class GetUserFollowers(BaseModel):
    username: str = Field(..., description="The users' username in Polarsteps")


class GetUserFollowees(BaseModel):
    username: str = Field(..., description="The users' username in Polarsteps")


class GetTrip(BaseModel):
    trip_id: int = Field(
        ..., description="The unique identifier of a trip in Polarsteps"
    )


# Define an enum for each eligible tool, this will be parsed as available MCP Tools
class PolarstepsTool(str, Enum):
    def __new__(cls, value: str, description: str, method: Type[BaseModel]):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj._description = description  # type: ignore
        obj._schema = method.model_json_schema()  # type: ignore
        return obj

    @property
    def description(self) -> str:
        return self._description  # type: ignore

    @property
    def schema(self) -> dict[str, Any]:
        """Get the JSON schema for this tool's input model."""
        return self._schema  # type: ignore

    USER = "get_user", "Shows all the users' polarstep information", GetUser
    USER_STATS = "get_user_stats", "Shows the users' travel statistics", GetUserStats
    USER_TRIPS = (
        "get_user_trips",
        "Shows a highlight of the users' latest N trips",
        GetUserTrips,
    )
    USER_FOLLOWERS = (
        "get_user_followers",
        "Show the usernames who the user follows",
        GetUserFollowers,
    )
    USER_FOLLOWEES = (
        "get_user_followees",
        "Show the usernames which follow the user",
        GetUserFollowees,
    )
    TRIP = "get_trip", "Show a specific trip", GetTrip


def get_user(polarsteps_client: PolarstepsClient, username: str) -> User:
    api_response = polarsteps_client.get_user_by_username(username)
    if api_response.is_error or api_response.user is None:
        return User(
            id=-1, uuid="00000000-0000-4000-8000-000000000000", username="unknown"
        )
    return api_response.user


def get_trip(polarsteps_client: PolarstepsClient, trip_id: int) -> Trip:
    api_response = polarsteps_client.get_trip(str(trip_id))
    if api_response.is_error or api_response.trip is None:
        return Trip(id=-1, uuid="00000000-0000-4000-8000-000000000000")
    return api_response.trip


def get_top_trips(
    polarsteps_client: PolarstepsClient, username: str, max_trips: int
) -> str:
    user_data = get_user(polarsteps_client, username)
    trips = user_data.alltrips
    if trips is None:
        return "User has no available trip."
    parsed_trips = []
    n_trips = int(max_trips)  # todo - catch errors
    for trip in trips[:n_trips]:
        start = datetime.fromtimestamp(trip.start_date)
        end = datetime.fromtimestamp(trip.end_date)
        days = (end - start).days
        parsed_trips.append(
            f"[ID:{trip.id}] {trip.display_name or trip.name} {days} days from {start.strftime('%Y/%m/%d')} to {end.strftime('%Y/%m/%d')}. {trip.step_count} steps across {int(trip.total_km):,}km!"
        )
    trips_string = "".join(f"\t{trip}\n" for trip in parsed_trips)
    return f"Top {n_trips} trips:\n{trips_string}"


async def serve() -> None:
    server = Server("polarsteps-mcp")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=tool.value,
                description=tool.description,
                inputSchema=tool.schema,
            )
            for tool in PolarstepsTool
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        # For all commands, we need an existing client
        # todo - initialize this as part of the server so it's not generated at each tool-call
        client = PolarstepsClient()

        match name:
            case PolarstepsTool.USER:
                user_data = get_user(client, arguments["username"])
                return [TextContent(type="text", text=f"User data:\n{user_data}")]

            case PolarstepsTool.USER_STATS:
                user_data = get_user(client, arguments["username"])
                return [
                    TextContent(type="text", text=f"User stats:\n{user_data.stats}")
                ]

            case PolarstepsTool.USER_FOLLOWERS:
                user_data = get_user(client, arguments["username"])
                return [
                    TextContent(
                        type="text", text=f"User is followed by:\n{user_data.followers}"
                    )
                ]

            case PolarstepsTool.USER_FOLLOWEES:
                user_data = get_user(client, arguments["username"])
                return [
                    TextContent(
                        type="text", text=f"User is followed by:\n{user_data.followees}"
                    )
                ]

            case PolarstepsTool.TRIP:
                user_data = get_trip(client, arguments["trip_id"])
                return [TextContent(type="text", text=f"Trip data:\n{user_data}")]

            case PolarstepsTool.USER_TRIPS:
                top_trips = get_top_trips(
                    client, arguments["username"], arguments["max_trips"]
                )
                return [TextContent(type="text", text=top_trips)]

            case _:
                raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


def main() -> None:
    """Entry point for the MCP server."""
    import asyncio

    asyncio.run(serve())
