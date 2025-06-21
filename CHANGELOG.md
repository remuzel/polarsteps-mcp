# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-06-21

### Added
- Initial release of Polarsteps MCP Server
- MCP tools for interacting with Polarsteps API:
  - `get_trip(trip_id)` - Get detailed trip information
  - `get_user(username)` - Get user profile and statistics
  - `get_user_trips(username)` - List all trips for a user
  - `search_trips(query)` - Search functionality (placeholder)
- MCP resources:
  - `polarsteps://config` - Server configuration information
  - `polarsteps://help` - Help documentation
- Environment-based configuration with POLARSTEPS_REMEMBER_TOKEN
- Comprehensive error handling and logging
- Full test suite with 9 test cases
- Command-line interface via `polarsteps-mcp` command
- Claude Desktop integration examples
- Professional documentation and packaging

### Technical Features
- Built with modern Python (3.8+) and uv package manager
- Uses MCP 1.0+ protocol specification
- Integrates with existing polarsteps-api package
- Comprehensive type hints and validation
- Production-ready error handling
- MIT license for open source use