from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from polarsteps_api import PolarstepsClient

from polarsteps_mcp.tools import (
    GetTravelStats,
    GetTripInput,
    GetTripLogInput,
    GetTripsInput,
    GetUserInput,
    PolarstepsTool,
    SearchTripsInput,
    get_travel_stats,
    get_trip,
    get_trip_log,
    get_trips,
    get_user,
    search_trips,
)


async def serve() -> None:
    server = Server("polarsteps-mcp")

    client = PolarstepsClient()

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
    async def call_tool(name: str, args: dict) -> list[TextContent]:
        match name:
            case PolarstepsTool.USER:
                input = GetUserInput(**args)
                return get_user(client, input)

            case PolarstepsTool.TRAVEL_STATS:
                input = GetTravelStats(**args)
                return get_travel_stats(client, input)

            case PolarstepsTool.TRIP:
                input = GetTripInput(**args)
                return get_trip(client, input)

            case PolarstepsTool.TRIP_LOG:
                input = GetTripLogInput(**args)
                return get_trip_log(client, input)

            case PolarstepsTool.TRIPS:
                input = GetTripsInput(**args)
                return get_trips(client, input)

            case PolarstepsTool.SEARCH_TRIPS:
                input = SearchTripsInput(**args)
                return search_trips(client, input)

            case _:
                raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):  # type: ignore
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


def main() -> None:
    """Entry point for the MCP server."""
    import asyncio

    asyncio.run(serve())
