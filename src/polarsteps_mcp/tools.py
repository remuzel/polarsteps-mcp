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
class GetUserProfile(BaseModel):
    username: str = Field(
        ...,
        description="The username of the Polarstep user to look for.",
    )


def get_user_profile(
    polarsteps_client: PolarstepsClient, input: GetUserProfile
) -> list[TextContent]:
    user = _get_user(polarsteps_client, input.username)
    if user.id == -1:
        return single_text_content(
            f"User not found: No Polarsteps user exists with username={input.username}. Please verify the username is correct and the user's profile is public."
        )
    return single_text_content(user.to_profile())


class GetUserSocial(BaseModel):
    username: str = Field(
        ...,
        description="The username of the Polarstep user to look for.",
    )


def get_user_social(
    polarsteps_client: PolarstepsClient, input: GetUserSocial
) -> list[TextContent]:
    user = _get_user(polarsteps_client, input.username)
    if user.id == -1:
        return single_text_content(
            f"User not found: No Polarsteps user exists with username={input.username}. Please verify the username is correct and the user's profile is public."
        )
    return single_text_content(user.to_social())


class GetUserStats(BaseModel):
    username: str = Field(
        ...,
        description="The username of the Polarstep user to look for.",
    )


def get_user_stats(
    polarsteps_client: PolarstepsClient, input: GetUserStats
) -> list[TextContent]:
    user = _get_user(polarsteps_client, input.username)
    if user.stats is None:
        return single_text_content(
            f"No travel stats found for username={input.username}"
        )
    return single_text_content(user.stats)


class GetTripInput(BaseModel):
    trip_id: int = Field(
        ...,
        description="The unique numerical identifier of a Polarsteps trip (typically 7+ digits)",
        ge=1_000_000,
    )
    n_steps: int = Field(
        5,
        ge=0,
        description="Maximum number of trip steps/locations to include in the response (each step contains photos and descriptions from specific locations).",
    )


def get_trip(
    polarsteps_client: PolarstepsClient, input: GetTripInput
) -> list[TextContent]:
    trip = _get_trip(polarsteps_client, input.trip_id)
    if trip.id == -1:
        return single_text_content(f"Could not find trip with ID: {input.trip_id}")
    return single_text_content(trip.to_detailed_summary(input.n_steps))


class GetTripLogInput(BaseModel):
    trip_id: int = Field(
        ...,
        description="The unique numerical identifier of a Polarsteps trip (typically 7+ digits)",
        ge=1_000_000,
    )


def get_trip_log(
    polarsteps_client: PolarstepsClient, input: GetTripLogInput
) -> list[TextContent]:
    trip = _get_trip(polarsteps_client, input.trip_id)
    if trip.id == -1:
        return single_text_content(f"Could not find trip with ID: {input.trip_id}")
    if trip.all_steps is None:
        return single_text_content(
            f"Trip with ID {input.trip_id} does not have any logged steps"
        )

    trip_log = [
        {
            "timestamp": step.timestamp,
            "title": step.name,
            "description": step.description,
            "location": f"{step.location.name} ({step.location.country_code})"
            if step.location
            else "Unknown",
        }
        for step in trip.all_steps
        if step.name is not None
    ]
    return [TextContent(type="text", text=json.dumps(trip)) for trip in trip_log]


class GetTripsInput(BaseModel):
    username: str = Field(
        ..., description="The Polarsteps username whose trips you want to retrieve"
    )
    n_trips: int = Field(
        5,
        ge=1,
        description="Maximum number of recent trips to return (ordered by most recent first)",
    )


def get_trips(
    polarsteps_client: PolarstepsClient, input: GetTripsInput
) -> list[TextContent]:
    user = _get_user(polarsteps_client, input.username)
    if user.alltrips is None:
        return single_text_content(
            f"No trips found for user with username={input.username}"
        )
    return [
        TextContent(type="text", text=json.dumps(trip.to_summary()))
        for trip in user.alltrips[: input.n_trips]
    ]


class SearchTripsInput(BaseModel):
    username: str = Field(
        ...,
        description="The Polarsteps username whose trips you want to search through",
    )
    name_query: str = Field(
        ...,
        description="Search term to match against trip names/titles (supports partial matching and fuzzy search)",
    )


def search_trips(polarsteps_client: PolarstepsClient, input: SearchTripsInput):
    user = _get_user(polarsteps_client, input.username)
    if user.alltrips is None:
        return single_text_content(
            f"No trips found for user with username={input.username}"
        )

    matched_trips = fuzzy_search_items(
        user.alltrips, input.name_query, field_name="name"
    )
    matched_trips.extend(
        fuzzy_search_items(user.alltrips, input.name_query, field_name="summary")
    )

    return [
        TextContent(type="text", text=trip.model_dump_json(include={"id", "name"}, exclude_none=True))
        for trip, _ in matched_trips
    ]


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

    USER_PROFILE = (
        "get_user_profile",
        "Get a users' profile overview including their living location and their number of countries visited & trips.",
        GetUserProfile,
    )
    USER_SOCIAL = (
        "get_user_social",
        "Get a users' social information including: followers, followees, their count and if they're considered popular.",
        GetUserSocial,
    )
    USER_STATS = (
        "get_user_stats",
        "Get available travel statistics and metrics for a Polarsteps user, including countries visited, total distance traveled, trip counts, and detailed travel analytics. Perfect for getting a complete picture of someone's travel history and achievements.",
        GetUserStats,
    )
    TRIP = (
        "get_trip",
        "Get comprehensive details about a specific trip including summary, timeline, route information, individual steps/locations, weather data, and engagement metrics. Use after get_trip_log when you need detailed information about specific locations or comprehensive trip data.",
        GetTripInput,
    )
    TRIP_LOG = (
        "get_trip_log",
        "Get an overview of the specific trip; this includes just a list of summarized steps, each including timestamp/title/description/location. Use this first for trip overviews before diving into detailed information.",
        GetTripLogInput,
    )
    TRIPS = (
        "get_trips",
        "Fetch a list of a user's recent trips with summary information including trip names, dates, duration, and basic stats. Ideal for browsing someone's travel history or finding trip IDs for detailed exploration. Use n_trips parameter to control how many recent trips to retrieve (default: 5).",
        GetTripsInput,
    )
    SEARCH_TRIPS = (
        "search_trips",
        "Search through a user's trips by name/title using fuzzy matching to find specific trips. Ideal for finding trips by destination (e.g., 'japan', 'italy'), themes (e.g., 'honeymoon', 'business'), or partial name matches. Supports flexible search terms that don't need to match exactly - the fuzzy matching will find relevant trips even with approximate spelling or partial keywords. **Use this as the first step when looking for specific trips by destination, theme, or name.**",
        SearchTripsInput,
    )
