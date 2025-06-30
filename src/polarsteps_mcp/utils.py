from typing import Any, List, Optional, Tuple

from mcp.types import TextContent
from polarsteps_api import PolarstepsClient
from polarsteps_api.models import Trip, User
from rapidfuzz import fuzz, process


def single_text_content(text: str) -> list[TextContent]:
    return [TextContent(type="text", text=text)]


def fuzzy_search_items(
    items: List[Any],
    query: str,
    field_name: str = "name",
    threshold: int = 60,
    limit: Optional[int] = None
) -> List[Tuple[Any, int]]:
    """
    Fuzzy search items by a specific field.

    Args:
        items: List of objects/dicts to search through
        query: Search query string
        field_name: Field to search in (default: "name")
        threshold: Minimum similarity score (0-100)
        limit: Maximum number of results to return

    Returns:
        List of tuples (item, score) sorted by relevance
    """
    if not items or not query.strip():
        return []

    # Extract field values for searching
    field_values = []
    for item in items:
        if hasattr(item, field_name):
            field_values.append(getattr(item, field_name))
        elif isinstance(item, dict) and field_name in item:
            field_values.append(item[field_name])
        else:
            field_values.append("")

    # Perform fuzzy matching
    matches = process.extract(
        query,
        field_values,
        scorer=fuzz.partial_ratio,
        limit=limit
    )

    # Filter by threshold and return with original items
    results = []
    for _match_text, score, index in matches:
        if score >= threshold:
            results.append((items[index], score))

    return results

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
