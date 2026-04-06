.PHONY: run test deploy lint format

run:
	docker-compose up

test:
	pytest tests/ -v --cov=orchestration --cov-report=term

lint:
	ruff check . && mypy .

format:
	ruff format .

deploy-staging:
	./scripts/deploy_staging.sh
