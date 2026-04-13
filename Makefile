.PHONY: run install clean format lint backup check help dev

# Application entry point
APP := main.py

# Data directory
DATA_DIR := data

help:
	@echo "Time Tracker - Available Commands:"
	@echo ""
	@echo "  make run          - Run the time tracker application"
	@echo "  make install      - Install dependencies with uv"
	@echo "  make clean        - Remove Python cache files"
	@echo "  make backup       - Backup time entries to timestamped file"
	@echo "  make check        - Validate data file integrity"
	@echo "  make format       - Format code with black"
	@echo "  make lint         - Lint code with flake8 (if installed)"
	@echo ""

run:
	@echo "Starting Time Tracker..."
	@uv run $(APP)

install:
	@echo "Installing dependencies with uv..."
	@uv pip install textual

dev:
	@echo "Starting Time Tracker in development mode..."
	@uv run python $(APP)

clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"

backup:
	@echo "Creating backup..."
	@mkdir -p backups
	@cp $(DATA_DIR)/entries.json backups/entries_$(shell date +%Y%m%d_%H%M%S).json
	@echo "Backup created in backups/ directory"

format:
	@echo "Formatting code..."
	@uv run black . || echo "Install black: uv pip install black"

lint:
	@echo "Linting code with flake8..."
	@if uv run python -c "import flake8" 2>/dev/null; then \
		uv run flake8 . --max-line-length=100 --ignore=E203,W503; \
	else \
		echo "flake8 not installed. Run: uv pip install flake8"; \
	fi

# Quick check of data file integrity
check:
	@echo "Checking data file..."
	@uv run python -c "import json; json.load(open('$(DATA_DIR)/entries.json'))" && echo "✓ Data file is valid JSON" || echo "✗ Data file has errors"
