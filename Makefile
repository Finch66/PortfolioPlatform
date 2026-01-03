.PHONY: up down logs test lint build

up:
	@docker compose up --build

down:
	@docker compose down

logs:
	@docker compose logs -f

test:
	@cd services/transaction && pytest

lint:
	@echo "No linters configured yet"

build:
	@docker compose build
