# Polarsteps MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that provides tools for interacting with the Polarsteps API. This enables Claude and other MCP clients to fetch travel data, trip information, and user profiles from Polarsteps.

## Features

- **Trip Information**: Get detailed information about Polarsteps trips including route, photos, and statistics
- **User Profiles**: Fetch user information, trip lists, and social connections
- **MCP Resources**: Access configuration and help documentation through MCP resources
- **Error Handling**: Comprehensive error handling with helpful error messages
- **Logging**: Built-in logging for debugging and monitoring

## Available Tools

### get_trip(trip_id)
Get detailed information about a specific trip.

**Parameters:**
- trip_id (string): The ID of the trip to retrieve

**Returns:** Trip details including name, summary, distance, steps, photos, and more.

### get_user(username)
Get user profile information by username.

**Parameters:**
- username (string): The username of the user to retrieve

**Returns:** User profile including name, location, trip count, followers, and more.

### get_user_trips(username)
Get all trips for a specific user.

**Parameters:**
- username (string): The username of the user whose trips to retrieve

**Returns:** List of all trips for the user with basic information.

### search_trips(query)
Search for trips (placeholder implementation).

**Parameters:**
- query (string): Search query for trip names or descriptions

**Note:** This is currently a placeholder. The base Polarsteps API doesn't include search functionality yet.

## Installation

### From Source

1. Clone or download this repository
2. Install the package:

```bash
cd polarsteps_mcp
uv sync
```

### From PyPI (when published)

```bash
pip install polarsteps-mcp
```

## Configuration

The server requires a Polarsteps remember token for authentication. You can obtain this from your browser's cookies when logged into Polarsteps.

### Environment Variables

- POLARSTEPS_REMEMBER_TOKEN: Your Polarsteps remember token (required)
- POLARSTEPS_BASE_URL: Base URL for Polarsteps API (default: https://www.polarsteps.com)

### Example

```bash
export POLARSTEPS_REMEMBER_TOKEN="your_remember_token_here"
```

## Usage

### Running the Server

```bash
# Using the installed script
polarsteps-mcp

# Or using Python module
python -m polarsteps_mcp.server
```

### Using with Claude Desktop

Add the server to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "polarsteps": {
      "command": "polarsteps-mcp",
      "env": {
        "POLARSTEPS_REMEMBER_TOKEN": "your_remember_token_here"
      }
    }
  }
}
```

### Using with Other MCP Clients

The server implements the standard MCP protocol and can be used with any compatible client. See the [MCP documentation](https://modelcontextprotocol.io/) for more details.

## Getting Your Remember Token

To use this MCP server, you need a Polarsteps remember token:

1. Log into Polarsteps in your web browser
2. Open browser developer tools (F12)
3. Go to Application/Storage -> Cookies
4. Find the remember_token cookie value
5. Copy this value and set it as the POLARSTEPS_REMEMBER_TOKEN environment variable

**Note:** Keep your remember token secure and don't share it publicly.

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd polarsteps_mcp

# Install development dependencies
uv sync --dev
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
# Format code
uv run black polarsteps_mcp/

# Lint code  
uv run ruff check polarsteps_mcp/

# Type checking
uv run mypy polarsteps_mcp/
```

## License

This project is licensed under the MIT License.

## Support

If you encounter any issues or have questions:

1. Check the logs for error messages
2. Verify your remember token is valid
3. Ensure you have network connectivity to Polarsteps
4. Open an issue on the repository