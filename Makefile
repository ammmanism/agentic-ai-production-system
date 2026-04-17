.PHONY: install run test deploy lint format build clean

install:
	uv pip install -e .

run:
	docker-compose up

test:
	pytest tests/ -v --cov=orchestration --cov-report=term

lint:
	ruff check . && mypy .

format:
	ruff format .

build:
	docker build -t agentic-system .

deploy-staging:
	./scripts/deploy_staging.sh

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .coverage coverage.xml
