from mcp.types import TextContent
from polarsteps_api import PolarstepsClient
from polarsteps_api.models import Trip, User


def single_text_content(text: str) -> list[TextContent]:
    return [TextContent(type="text", text=text)]


def _get_user(polarsteps_client: PolarstepsClient, username: str) -> User:
    api_response = polarsteps_client.get_user_by_username(username)
    if api_response.is_error or api_response.user is None:
        return User(
            id=-1, uuid="00000000-0000-4000-8000-000000000000", username="unknown"
        )
    return api_response.user


def _get_trip(polarsteps_client: PolarstepsClient, trip_id: int) -> Trip:
    api_response = polarsteps_client.get_trip(str(trip_id))
    if api_response.is_error or api_response.trip is None:
        return Trip(id=-1, uuid="00000000-0000-4000-8000-000000000000")
    return api_response.trip
