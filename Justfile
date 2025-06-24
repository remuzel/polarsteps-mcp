# Install just: https://github.com/casey/just

# Default recipe
default:
    @just --list

setup:
    @echo "🚀 Setting up development environment..."
    uv sync --dev
    uv run pre-commit install
    @echo "✅ Setup complete!"

# Lint code
lint:
    @echo "🔍 Linting code..."
    uv run ruff check --fix --unsafe-fixes src tests
    @echo "🔍 Type checking..."
    uv run mypy src
    @echo "✅ Lint complete!"

# Run tests
test:
    @echo "🧪 Running tests..."
    uv run pytest tests/ -v
    @echo "✅ Tests complete!"

# Test MCP server with inspector
test-mcp:
    @echo "🔍 Testing MCP server with inspector..."
    npx @modelcontextprotocol/inspector uv run src/polarsteps-mcp

# Run the MCP server directly
run:
    @echo "🚀 Running MCP server..."
    uv run polarsteps-mcp

# Clean up generated files
clean:
    @echo "🧹 Cleaning up..."
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -rf .coverage
    rm -rf dist
    rm -rf build
    rm -rf *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    @echo "✅ Complete!"

# Build package
build:
    @echo "📦 Building package..."
    uv build

    @echo "✅ Build complete!"

# Update dependencies
update:
    @echo "🔄 Updating dependencies..."
    uv lock --upgrade

    @echo "✅ Done complete!"
