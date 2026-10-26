.PHONY: setup migrate test lint format dev dev-backend dev-frontend

setup:
	cd backend && uv sync
	cd frontend && pnpm install --frozen-lockfile
	$(MAKE) migrate

migrate:
	cd backend && uv run alembic upgrade head

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
	cd backend && uv run uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && pnpm dev
