.PHONY: install run test deploy lint format build clean dev api streamlit

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

dev:
	@echo "Starting API and Streamlit together..."
	@(cd entrypoints/api && uvicorn main:app --reload --port 8000 &)
	@(cd entrypoints/frontend && streamlit run app.py --server.port 8501 &)
	@wait

dev-concurrently:
	npx concurrently "make api" "make streamlit"

api:
	cd entrypoints/api && uvicorn main:app --reload --port 8000

streamlit:
	cd entrypoints/frontend && streamlit run app.py --server.port 8501
