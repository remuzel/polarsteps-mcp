# Polarsteps MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that enables Claude and other AI assistants to access Polarsteps travel data. Query user profiles, trip details, travel statistics, and search through travel histories with natural language.

[![smithery badge](https://smithery.ai/badge/@remuzel/polarsteps-mcp)](https://smithery.ai/server/@remuzel/polarsteps-mcp)


## Features

- **User Profiles**: Get profile info, social stats, and travel metrics
- **Trip Data**: Access detailed trip information, timelines, and locations
- **Smart Search**: Find trips by destination, theme, or keywords with fuzzy matching
- **Travel Analytics**: Retrieve comprehensive travel statistics and achievements

## Quick Start

Until I add it to PyPI, the quickest way to get started is using [Smithery](https://smithery.ai/server/@remuzel/polarsteps-mcp):


```bash
npx -y @smithery/cli install @remuzel/polarsteps-mcp --client claude
```

Then configure your Polarsteps token.

## Configuration

You'll need your Polarsteps `remember_token` to authenticate API requests.

### Getting Your Token

1. Go to https://www.polarsteps.com/ and make sure you're logged in
2. Open your browser's Dev Tools:
   - **Firefox**: Shift+F9 → Storage tab
   - **Chrome**: F12 → Application tab → Cookies
3. Find the `remember_token` cookie for https://www.polarsteps.com
4. Copy the token value

### Setting the Token

Set your token as an environment variable:

```bash
export POLARSTEPS_REMEMBER_TOKEN="your_remember_token_here"
```

## Usage

### With Claude Desktop

Add this configuration to your Claude Desktop settings:

```json
{
  "mcpServers": {
    "polarsteps": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/remuzel/polarsteps-mcp", "polarsteps-mcp"],
      "env": {
        "POLARSTEPS_REMEMBER_TOKEN": "your_remember_token_here"
      }
    }
  }
}
```

### Example Queries

Once configured, you can ask Claude things like:
- "Show me travel stats for username 'johndoe'"
- "Tell me about johndoe's trip to Japan"
- "What country should johndoe add to their bucketlist?"

### Local Testing

Test the MCP server locally with the inspector:

```bash
npx @modelcontextprotocol/inspector uvx --from git+https://github.com/remuzel/polarsteps-mcp polarsteps-mcp
```

## Installation from Source

For development or manual installation:

```bash
# Clone the repository
git clone https://github.com/remuzel/polarsteps-mcp
cd polarsteps-mcp

# Setup development environment
just setup
# or without just:
uv sync --dev && uv pip install -e .
```

## Development

### Running Tests

```bash
just test
```

### Local MCP Testing

```bash
just test-mcp
```

### Code Formatting

```bash
just lint
```

## ⚠️ Legal Notice

This MCP server uses the [`polarsteps-api`](https://github.com/remuzel/polarsteps-api) package to access Polarsteps data through undocumented APIs.

**Important**: Please read the full legal disclaimer and terms of use in the [polarsteps-api package](https://github.com/remuzel/polarsteps-api#%EF%B8%8F-important-disclaimers) before using this tool.

By using this MCP server, you agree to the terms outlined in the API package and acknowledge the associated risks.
