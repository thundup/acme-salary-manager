# Single image: the built React app served by FastAPI, with SQLite seeded on start.
FROM node:24-slim AS ui
WORKDIR /ui
RUN npm install --global pnpm@11.22.0
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm build

FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"
COPY backend/pyproject.toml backend/uv.lock backend/.python-version ./
RUN uv sync --locked --no-dev --no-install-project
COPY backend/ ./
COPY --from=ui /ui/dist ./static

RUN useradd --create-home acme && mkdir /data && chown acme /data
USER acme
ENV STATIC_DIR=/app/static \
    DATABASE_URL=sqlite:////data/acme.db \
    PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && python -m app.seed && exec uvicorn app.main:app --host 0.0.0.0 --port \"$PORT\""]
