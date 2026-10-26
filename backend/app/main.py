from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import employees, health, insights, reference
from app.api.errors import register_error_handlers
from app.config import get_settings


def create_app(static_dir: Path | None = None) -> FastAPI:
    app = FastAPI(title="ACME Salary Manager")
    register_error_handlers(app)
    app.include_router(health.router, prefix="/api")
    app.include_router(employees.router, prefix="/api")
    app.include_router(insights.router, prefix="/api")
    app.include_router(reference.router, prefix="/api")
    if static_dir is not None:
        _serve_ui(app, static_dir)
    return app


def _serve_ui(app: FastAPI, static_dir: Path) -> None:
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")
    index = static_dir / "index.html"

    @app.get("/{path:path}", include_in_schema=False)
    def app_shell(path: str) -> FileResponse:
        if path.startswith("api/"):
            raise HTTPException(status_code=404)
        candidate = (static_dir / path).resolve()
        if path and candidate.is_file() and candidate.is_relative_to(static_dir.resolve()):
            return FileResponse(candidate)
        return FileResponse(index)


app = create_app(get_settings().static_dir)
