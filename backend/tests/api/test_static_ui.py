from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def ui_client(tmp_path: Path) -> TestClient:
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<div id='root'></div>")
    (tmp_path / "assets" / "app.js").write_text("console.log('ui')")
    return TestClient(create_app(static_dir=tmp_path))


def test_serves_built_assets(ui_client: TestClient) -> None:
    response = ui_client.get("/assets/app.js")

    assert response.status_code == 200
    assert "console.log" in response.text


@pytest.mark.parametrize("path", ["/", "/employees", "/insights"])
def test_client_side_routes_get_the_app_shell(ui_client: TestClient, path: str) -> None:
    response = ui_client.get(path)

    assert response.status_code == 200
    assert "id='root'" in response.text


def test_unknown_api_paths_stay_json_404s(ui_client: TestClient) -> None:
    response = ui_client.get("/api/nope")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")


def test_api_still_works_alongside_the_ui(ui_client: TestClient) -> None:
    assert ui_client.get("/api/reference").status_code == 200


def test_does_not_serve_files_outside_the_ui_folder(tmp_path: Path) -> None:
    ui = tmp_path / "ui"
    (ui / "assets").mkdir(parents=True)
    (ui / "index.html").write_text("shell")
    (tmp_path / "secret.txt").write_text("do not serve")
    client = TestClient(create_app(static_dir=ui))

    response = client.get("/..%2Fsecret.txt")

    assert "do not serve" not in response.text
