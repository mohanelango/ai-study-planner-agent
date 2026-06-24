.PHONY: up down logs backend-shell frontend-shell test lint format

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

backend-shell:
	docker compose exec backend sh

frontend-shell:
	docker compose exec frontend sh

test:
	docker compose run --rm backend python -m compileall app

lint:
	docker compose run --rm frontend npm run lint

format:
	@echo "No formatter configured for Weekend 1."
