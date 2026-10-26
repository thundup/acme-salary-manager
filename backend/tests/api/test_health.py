from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.db import get_session


class UnreachableDatabaseSession:
    def execute(self, *_: object) -> None:
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))


def test_health_reports_ok_when_database_is_reachable(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_returns_503_when_database_is_unreachable(client: TestClient) -> None:
    app = client.app
    assert isinstance(app, FastAPI)
    app.dependency_overrides[get_session] = UnreachableDatabaseSession

    response = client.get("/api/health")

    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "database": "unreachable"}
