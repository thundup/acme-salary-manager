BACKEND_PORT ?= 8000
FRONTEND_PORT ?= 5173

.PHONY: setup migrate seed test lint format dev dev-backend dev-frontend

setup:
	cd backend && uv sync
	cd frontend && pnpm install --frozen-lockfile
	$(MAKE) migrate

migrate:
	cd backend && uv run alembic upgrade head

seed:
	cd backend && uv run python -m app.seed $(ARGS)

test:
	cd backend && uv run pytest
	cd frontend && pnpm test

lint:
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy app tests
	cd frontend && pnpm lint && pnpm format:check && pnpm typecheck

format:
	cd backend && uv run ruff check --fix . && uv run ruff format .
	cd frontend && pnpm format

dev:
	$(MAKE) -j2 dev-backend dev-frontend

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload --port $(BACKEND_PORT)

dev-frontend:
	cd frontend && API_TARGET=http://127.0.0.1:$(BACKEND_PORT) pnpm dev --port $(FRONTEND_PORT) --strictPort
