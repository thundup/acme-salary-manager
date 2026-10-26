from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import add_employee


def test_updates_only_the_fields_sent(client: TestClient, session: Session) -> None:
    employee = add_employee(session, full_name="Lena Vogel", salary_minor=500)

    response = client.patch(f"/api/employees/{employee.id}", json={"salary_minor": 650})

    assert response.status_code == 200
    assert response.json()["salary_minor"] == 650
    assert response.json()["full_name"] == "Lena Vogel"


def test_bonus_can_be_cleared_with_null(client: TestClient, session: Session) -> None:
    employee = add_employee(session, bonus_minor=1_000)

    response = client.patch(f"/api/employees/{employee.id}", json={"bonus_minor": None})

    assert response.status_code == 200
    assert response.json()["bonus_minor"] is None


def test_required_fields_cannot_be_nulled(client: TestClient, session: Session) -> None:
    employee = add_employee(session)

    response = client.patch(f"/api/employees/{employee.id}", json={"salary_minor": None})

    assert response.status_code == 422
    assert response.json()["error"]["fields"] == {"salary_minor": "Cannot be empty"}


def test_rules_apply_to_the_merged_record(client: TestClient, session: Session) -> None:
    employee = add_employee(session, department="Engineering", job_title="Principal Engineer")

    response = client.patch(f"/api/employees/{employee.id}", json={"department": "Finance"})

    assert response.status_code == 422
    assert response.json()["error"]["fields"] == {
        "job_title": "'Principal Engineer' is not a job title in Finance"
    }


def test_email_must_stay_unique(client: TestClient, session: Session) -> None:
    add_employee(session, email="taken@acme-corp.com")
    employee = add_employee(session, email="mine@acme-corp.com")

    clash = client.patch(f"/api/employees/{employee.id}", json={"email": "TAKEN@acme-corp.com"})
    own = client.patch(f"/api/employees/{employee.id}", json={"email": "mine@acme-corp.com"})

    assert clash.status_code == 409
    assert own.status_code == 200


def test_employee_code_is_immutable(client: TestClient, session: Session) -> None:
    employee = add_employee(session)

    response = client.patch(f"/api/employees/{employee.id}", json={"employee_code": "ACME-999999"})

    assert response.status_code == 422


def test_terminated_employees_cannot_be_edited(client: TestClient, session: Session) -> None:
    employee = add_employee(session, status="terminated")

    response = client.patch(f"/api/employees/{employee.id}", json={"salary_minor": 1})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "employee_terminated"


def test_updating_an_unknown_employee_is_a_404(client: TestClient) -> None:
    assert client.patch("/api/employees/999", json={"salary_minor": 1}).status_code == 404
