.PHONY: install dev test lint format clean docker-build docker-run deploy docs help

install:
	@pip install -e ".[dev,test]"

dev:
	@# run development server with hot reload
	@echo "Running development server with hot reload..."
	@# command to run development server

test:
	@# pytest with coverage report
	@echo "Running tests with coverage report..."
	@pytest --cov=.

lint:
	@# ruff check + mypy
	@echo "Running linter checks..."
	@ruff .
	@mypy .

format:
	@# ruff format + isort
	@echo "Formatting code..."
	@ruff --fix .
	@isort .

clean:
	@# remove __pycache__, .mypy_cache, dist/
	@echo "Cleaning up..."
	@rm -rf __pycache__
	@rm -rf .mypy_cache
	@rm -rf dist

docker-build:
	@# docker build
	@echo "Building Docker image..."
	@docker build -t agentic-ai-production-system .

docker-run:
	@# docker compose up
	@echo "Running Docker container..."
	@docker compose up

deploy:
	@# deploy to staging
	@echo "Deploying to staging..."
	@# command to deploy to staging

docs:
	@# generate docs with mkdocs
	@echo "Generating documentation..."
	@mkdocs build

help:
	@echo "Available targets:"
	@echo "  install        - pip install -e '.[dev,test]'"
	@echo "  dev            - run development server with hot reload"
	@echo "  test           - pytest with coverage report"
	@echo "  lint           - ruff check + mypy"
	@echo "  format         - ruff format + isort"
	@echo "  clean          - remove __pycache__, .mypy_cache, dist/"
	@echo "  docker-build   - docker build"
	@echo "  docker-run     - docker compose up"
	@echo "  deploy         - deploy to staging"
	@echo "  docs           - generate docs with mkdocs"
	@echo "  help           - print available commands"