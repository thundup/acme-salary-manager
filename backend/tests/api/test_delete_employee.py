from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import add_employee


def test_delete_marks_the_employee_terminated(client: TestClient, session: Session) -> None:
    employee = add_employee(session)

    response = client.delete(f"/api/employees/{employee.id}")

    assert response.status_code == 204
    record = client.get(f"/api/employees/{employee.id}").json()
    assert record["status"] == "terminated"
    assert record["terminated_at"] is not None
    assert client.get("/api/employees").json()["total"] == 0


def test_deleting_twice_keeps_the_original_termination(
    client: TestClient, session: Session
) -> None:
    employee = add_employee(session)
    client.delete(f"/api/employees/{employee.id}")
    first = client.get(f"/api/employees/{employee.id}").json()["terminated_at"]

    response = client.delete(f"/api/employees/{employee.id}")

    assert response.status_code == 204
    assert client.get(f"/api/employees/{employee.id}").json()["terminated_at"] == first


def test_deleting_an_unknown_employee_is_a_404(client: TestClient) -> None:
    assert client.delete("/api/employees/999").status_code == 404
