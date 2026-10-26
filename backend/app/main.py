from fastapi import FastAPI

from app.api import employees, health
from app.api.errors import register_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="ACME Salary Manager")
    register_error_handlers(app)
    app.include_router(health.router, prefix="/api")
    app.include_router(employees.router, prefix="/api")
    return app


app = create_app()
