from fastapi.testclient import TestClient

from tests.factories import employee_payload


def test_creates_an_active_employee(client: TestClient) -> None:
    payload = employee_payload(email="Asha.Rao@ACME-CORP.com", bonus_minor=250_000_00)

    response = client.post("/api/employees", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["status"] == "active"
    assert body["email"] == "asha.rao@acme-corp.com"
    assert body["salary_minor"] == payload["salary_minor"]
    assert body["bonus_minor"] == 250_000_00
    assert body["terminated_at"] is None


def test_rejects_a_non_positive_salary(client: TestClient) -> None:
    response = client.post("/api/employees", json=employee_payload(salary_minor=0))

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert "salary_minor" in response.json()["error"]["fields"]


def test_rejects_a_negative_bonus(client: TestClient) -> None:
    response = client.post("/api/employees", json=employee_payload(bonus_minor=-1))

    assert response.status_code == 422
    assert "bonus_minor" in response.json()["error"]["fields"]


def test_rejects_a_malformed_email(client: TestClient) -> None:
    response = client.post("/api/employees", json=employee_payload(email="not-an-email"))

    assert response.status_code == 422
    assert "email" in response.json()["error"]["fields"]


def test_rejects_a_malformed_employee_code(client: TestClient) -> None:
    response = client.post("/api/employees", json=employee_payload(employee_code="123"))

    assert response.status_code == 422
    assert "employee_code" in response.json()["error"]["fields"]


def test_reports_domain_rule_violations_per_field(client: TestClient) -> None:
    payload = employee_payload(
        department="Finance", job_title="Senior Software Engineer", hire_date="2026-10-27"
    )

    response = client.post("/api/employees", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["fields"] == {
        "job_title": "'Senior Software Engineer' is not a job title in Finance",
        "hire_date": "Hire date cannot be in the future",
    }


def test_rejects_a_duplicate_email_regardless_of_case(client: TestClient) -> None:
    client.post("/api/employees", json=employee_payload(email="dup@acme-corp.com"))

    response = client.post("/api/employees", json=employee_payload(email="DUP@acme-corp.com"))

    assert response.status_code == 409
    assert response.json()["error"] == {
        "code": "duplicate_employee",
        "message": "An employee with this email already exists",
        "fields": {"email": "Already in use"},
    }


def test_rejects_a_duplicate_employee_code(client: TestClient) -> None:
    client.post("/api/employees", json=employee_payload(employee_code="ACME-900001"))

    response = client.post("/api/employees", json=employee_payload(employee_code="ACME-900001"))

    assert response.status_code == 409
    assert response.json()["error"]["fields"] == {"employee_code": "Already in use"}
