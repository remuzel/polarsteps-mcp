# Polarsteps MCP Server
[![smithery badge](https://smithery.ai/badge/@remuzel/polarsteps-mcp)](https://smithery.ai/server/@remuzel/polarsteps-mcp)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that provides tools for interacting with the Polarsteps API. This enables Claude and other MCP clients to fetch travel data, trip information, and user profiles from Polarsteps.

## Installation

### Installing via Smithery

To install polarsteps-mcp for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@remuzel/polarsteps-mcp):

```bash
npx -y @smithery/cli install @remuzel/polarsteps-mcp --client claude
```

### Manual Installation
```bash
just setup
# or without just
uv sync --dev && uv pip install -e .
```

## Configuration

Set your Polarsteps remember token as an environment variable:

```bash
export POLARSTEPS_REMEMBER_TOKEN="your_remember_token_here"
```

Get your token from browser cookies when logged into Polarsteps.

## Usage

### Running the Server

```bash
just test-mcp
# or
npx @modelcontextprotocol/inspector uv run polarsteps-mcp
```

### Using with Claude Desktop

Add to your Claude Desktop configuration:

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

## Development

```bash
# Run tests
just test

# Test the mcp-server locally
just test-mcp

# Format code
just lint
```

---

## ⚠️ Legal Notice

This MCP server uses the [`polarsteps-api`](https://github.com/remuzel/polarsteps-api) package to access Polarsteps data through undocumented APIs.

**Important**: Please read the full legal disclaimer and terms of use in the [polarsteps-api package](https://github.com/remuzel/polarsteps-api#%EF%B8%8F-important-disclaimers) before using this tool.

By using this MCP server, you agree to the terms outlined in the API package and acknowledge the associated risks.
