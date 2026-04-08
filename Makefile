```makefile
.PHONY: install dev test lint format clean docker-build docker-run deploy docs help

install:
	pip install -e ".[dev,test]"

dev:
	python -m uvicorn main:app --reload

test:
	pytest --cov=./ --cov-report=xml

lint:
	ruff check . && mypy .

format:
	ruff format . && isort .

clean:
	find . -type d -name "__pycache__" -exec rm -r {} + \
	find . -type d -name ".mypy_cache" -exec rm -r {} + \
	find . -type d -name "dist" -exec rm -r {} +

docker-build:
	docker build -t agentic-ai-production-system .

docker-run:
	docker compose up

deploy:
	kubectl apply -f k8s/staging/

docs:
	mkdocs build

help:
	@echo "Available commands:"
	@echo "  install        — pip install -e \"\".[dev,test]\"\""
	@echo "  dev            — run development server with hot reload"
	@echo "  test           — pytest with coverage report"
	@echo "  lint           — ruff check + mypy"
	@echo "  format         — ruff format + isort"
	@echo "  clean          — remove __pycache__, .mypy_cache, dist/"
	@echo "  docker-build   — docker build"
	@echo "  docker-run     — docker compose up"
	@echo "  deploy         — deploy to staging"
	@echo "  docs           — generate docs with mkdocs"
```