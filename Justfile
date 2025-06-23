# Install just: https://github.com/casey/just

# Default recipe
default:
    @just --list

setup:
    @echo "🚀 Setting up development environment..."
    uv sync --dev
    uv run pre-commit install
    @echo "✅ Setup complete!"

# Install dependencies
install:
    @echo "📦 Installing dependencies..."
    uv sync

# Install dev dependencies
install-dev:
    @echo "📦 Installing development dependencies..."
    uv sync --dev

# Lint code
lint:
    @echo "🔍 Linting code..."
    uv run ruff check --fix --unsafe-fixes polarsteps_mcp tests scripts

# Type check
typecheck:
    @echo "🔍 Type checking..."
    uv run mypy polarsteps_mcp

# Run tests
test:
    @echo "🧪 Running tests..."
    uv run pytest tests/ -v

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

# Build package
build:
    @echo "📦 Building package..."
    uv build

# Update dependencies
update:
    @echo "🔄 Updating dependencies..."
    uv lock --upgrade
