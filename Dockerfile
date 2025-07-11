# Generated by https://smithery.ai. See: https://smithery.ai/docs/build/project-config
# syntax=docker/dockerfile:1

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
 && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src ./src
COPY LICENSE.md ./
COPY README.md ./

# Install Python dependencies and package
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir .

# Default command runs the MCP server
CMD ["polarsteps-mcp"]
