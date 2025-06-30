import json
from enum import Enum
from typing import Any, Type

from mcp.types import TextContent
from polarsteps_api import PolarstepsClient
from pydantic import BaseModel, Field

from polarsteps_mcp.utils import (
    _get_trip,
    _get_user,
    fuzzy_search_items,
    single_text_content,
)


# For each tool you're going to use, define the interaction model (what parameters are required, their description, ...)
class GetUserInput(BaseModel):
    username: str = Field(..., description="The users' username in Polarsteps")


def get_user(
    polarsteps_client: PolarstepsClient, input: GetUserInput
) -> list[TextContent]:
    user = _get_user(polarsteps_client, input.username)
    if user.id == -1:
        return single_text_content(
            f"Could not find user with username: {input.username}"
        )
    return single_text_content(json.dumps(user.to_summary()))


class GetTravelStats(BaseModel):
    username: str = Field(..., description="The users' username in Polarsteps")


def get_travel_stats(
    polarsteps_client: PolarstepsClient, input: GetTravelStats
) -> list[TextContent]:
    user = _get_user(polarsteps_client, input.username)
    if user.stats is None:
        return single_text_content(
            f"User @{input.username} does not have travel stats"
        )
    return single_text_content(user.stats.model_dump_json())


class GetTripInput(BaseModel):
    trip_id: int = Field(
        ..., description="The unique identifier of a trip in Polarsteps", ge=1_000_000
    )
    n_steps: int = Field(
        5,
        description="Trips usually contain n≥0 steps set in a location with pictures and a description.",
    )


def get_trip(
    polarsteps_client: PolarstepsClient, input: GetTripInput
) -> list[TextContent]:
    trip = _get_trip(polarsteps_client, input.trip_id)
    if trip.id == -1:
        return single_text_content(f"Could not find trip with ID: {input.trip_id}")
    return single_text_content(json.dumps(trip.to_detailed_summary(input.n_steps)))

class GetTripsInput(BaseModel):
    username: str = Field(..., description="The users' username in Polarsteps")
    n_trips: int = Field(
        5,
        description="The number of trips to view",
    )


def get_trips(
    polarsteps_client: PolarstepsClient, input: GetTripsInput
) -> list[TextContent]:
    user = _get_user(polarsteps_client, input.username)
    if user.alltrips is None:
        return single_text_content(
            f"User @{input.username} does not have any trips!"
        )
    return [TextContent(type="text", text=json.dumps(trip.to_summary())) for trip in user.alltrips[:input.n_trips]]

class GetTripsByNameInput(BaseModel):
    username: str = Field(..., description="The users' username in Polarsteps")
    name_query: str = Field(..., description="Name to search by in trips")

def get_trips_by_name(polarsteps_client: PolarstepsClient, input: GetTripsByNameInput):
    user = _get_user(polarsteps_client, input.username)
    if user.alltrips is None:
        return single_text_content(
            f"User @{input.username} does not have any trips!"
        )

    matched_trips = fuzzy_search_items(user.alltrips, input.name_query, field_name="name")

    return [TextContent(type="text", text=trip.model_dump_json(include={"id", "name"})) for trip, _ in matched_trips]

# Define an enum for each available tool, this will be parsed by the MCP Server
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

    USER = "get_user", "Shows all the users' polarstep information", GetUserInput
    TRAVEL_STATS = (
        "get_travel_stats",
        "Shows the users' travel statistics",
        GetTravelStats,
    )
    TRIP = "get_trip", "Show a specific trip", GetTripInput
    TRIPS = (
        "get_trips",
        "Shows a highlight of the users' latest N trips",
        GetTripsInput,
    )
    TRIPS_BY_NAME = (
        "get_trips_by_name",
        "Search trips by name",
        GetTripsByNameInput
    )
