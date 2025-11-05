.PHONY: help install dev test lint format clean run

# Default target
help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  dev        - Set up development environment"
	@echo "  test       - Run tests"
	@echo "  lint       - Run code linting"
	@echo "  format     - Format code"
	@echo "  clean      - Clean cache files"
	@echo "  run        - Run the bot"

# Installation
install:
	poetry install

# Development setup
dev: install
	poetry run pre-commit install

# Testing
test:
	poetry run pytest -v

test-coverage:
	poetry run pytest --cov=cogs --cov=database --cov=utils --cov-report=html

# Code quality
lint:
	poetry run ruff check .
	poetry run mypy .

format:
	poetry run black .
	poetry run ruff format .

# Check all code quality (used in CI)
check: lint test

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build

# Run the bot
run:
	poetry run python bot.py

# Export requirements
requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

# Database migrations
migrate:
	poetry run alembic upgrade head

migration-generate:
	poetry run alembic revision --autogenerate -m "$(MSG)"

# Development server with auto-reload
dev-run:
	poetry run python bot.py --reload