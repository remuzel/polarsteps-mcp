from datetime import datetime
from enum import Enum
from typing import Any, Type

from mcp.types import TextContent
from polarsteps_api import PolarstepsClient
from pydantic import BaseModel, Field

from polarsteps_mcp.utils import _get_trip, _get_user, single_text_content


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
    return single_text_content(
        f"""
{user.first_name} {user.last_name}
""".strip()
    )


class GetUserStatsInput(BaseModel):
    username: str = Field(..., description="The users' username in Polarsteps")


def get_user_stats(
    polarsteps_client: PolarstepsClient, input: GetUserStatsInput
) -> list[TextContent]:
    user = _get_user(polarsteps_client, input.username)
    if user.stats is None:
        return single_text_content(
            f"Could not find user with username: {input.username}"
        )
    return single_text_content(user.stats.model_dump_json())


class GetUserTripsInput(BaseModel):
    username: str = Field(..., description="The users' username in Polarsteps")
    max_trips: int = Field(
        50,
        description="The maximum number of trips to return",
    )


def get_user_trips(
    polarsteps_client: PolarstepsClient, input: GetUserTripsInput
) -> list[TextContent]:
    user = _get_user(polarsteps_client, input.username)
    if user.alltrips is None:
        return single_text_content(
            f"Could not find user with username: {input.username}"
        )
    parsed_trips = []
    n_trips = int(input.max_trips)  # todo - catch parsing errors
    for trip in user.alltrips[:n_trips]:
        start = datetime.fromtimestamp(trip.start_date or 0)
        end = datetime.fromtimestamp(trip.end_date or 0)
        parsed_trips.append(
            f"[ID:{trip.id}] {trip.display_name or trip.name} {trip.length_days} from {start.strftime('%Y/%m/%d')} to {end.strftime('%Y/%m/%d')}. {trip.step_count} steps across {int(trip.total_km or 0):,}km!"
        )
    trips_string = "".join(f"\t{trip}\n" for trip in parsed_trips)
    return single_text_content(f"Top {n_trips} trips:\n{trips_string}")


class GetUserSocialStatusInput(BaseModel):
    username: str = Field(..., description="The users' username in Polarsteps")


def get_user_social_status(
    polarsteps_client: PolarstepsClient, input: GetUserSocialStatusInput
) -> list[TextContent]:
    user = _get_user(polarsteps_client, input.username)
    followers = user.followers
    followees = user.followees
    follow_requests = len(user.follow_requests or [])
    sent_follow_requests = len(user.sent_follow_requests or [])
    if followers is None or followees is None:
        return single_text_content(
            f"Customer with username {input.username} has incomplete social profile"
        )
    return single_text_content(
        f"""
{user.first_name} {user.last_name} follows {len(followers)} and is followed by {len(followees)}! They have {sent_follow_requests} outgoing requests, and {follow_requests} incoming...
""".strip()
    )


class GetTripInput(BaseModel):
    trip_id: int = Field(
        ..., description="The unique identifier of a trip in Polarsteps", ge=1_000_000
    )


def get_trip(
    polarsteps_client: PolarstepsClient, input: GetTripInput
) -> list[TextContent]:
    trip = _get_trip(polarsteps_client, input.trip_id)
    if trip.id == -1:
        return single_text_content(f"Could not find trip with ID: {input.trip_id}")
    try:
        step_1 = trip.all_steps[0].location  # type: ignore
        step_n = trip.all_steps[-1].location  # type: ignore
        first_step = f"{step_1.name} ({step_1.country})"  # type: ignore
        last_step = f"{step_n.name} ({step_n.country})"  # type: ignore
    except Exception:
        return single_text_content(
            f"""
{trip.name}! A {trip.length_days} long trip ({int(trip.total_km or 0):,}km).{f' In summary: {trip.summary}' if trip.summary is not None else ''}
""".strip()
        )
    return single_text_content(
        f"""
{trip.name}! A {trip.length_days} long trip from {first_step} to {last_step} ({int(trip.total_km or 0):,}km). In summary:
{trip.summary}
""".strip()
    )


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
    USER_STATS = (
        "get_user_stats",
        "Shows the users' travel statistics",
        GetUserStatsInput,
    )
    USER_TRIPS = (
        "get_user_trips",
        "Shows a highlight of the users' latest N trips",
        GetUserTripsInput,
    )
    USER_SOCIAL_STATUS = (
        "get_user_social_status",
        "Show the usernames who the user follows",
        GetUserSocialStatusInput,
    )
    TRIP = "get_trip", "Show a specific trip", GetTripInput
