from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import add_employee


def names(response: Any) -> list[str]:
    return [item["full_name"] for item in response.json()["items"]]


def test_gets_an_employee_by_id(client: TestClient, session: Session) -> None:
    employee = add_employee(session, full_name="Kenji Sato")

    response = client.get(f"/api/employees/{employee.id}")

    assert response.status_code == 200
    assert response.json()["full_name"] == "Kenji Sato"


def test_unknown_employee_is_a_404(client: TestClient) -> None:
    response = client.get("/api/employees/999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "employee_not_found"


def test_lists_employees_sorted_by_name_by_default(client: TestClient, session: Session) -> None:
    for name in ("Chen Wei", "Amara Obi", "Bea Lund"):
        add_employee(session, full_name=name)

    response = client.get("/api/employees")

    assert response.status_code == 200
    assert names(response) == ["Amara Obi", "Bea Lund", "Chen Wei"]
    assert response.json() | {"items": []} == {
        "items": [],
        "total": 3,
        "page": 1,
        "page_size": 25,
    }


def test_paginates_with_a_total_across_pages(client: TestClient, session: Session) -> None:
    for name in ("A", "B", "C"):
        add_employee(session, full_name=name)

    response = client.get("/api/employees", params={"page": 2, "page_size": 2})

    assert names(response) == ["C"]
    assert response.json()["total"] == 3


def test_sorts_by_salary_descending(client: TestClient, session: Session) -> None:
    add_employee(session, full_name="Low", salary_minor=100)
    add_employee(session, full_name="High", salary_minor=300)
    add_employee(session, full_name="Mid", salary_minor=200)

    response = client.get("/api/employees", params={"sort": "salary_minor", "order": "desc"})

    assert names(response) == ["High", "Mid", "Low"]


def test_filters_by_country_department_and_job_title(client: TestClient, session: Session) -> None:
    add_employee(session, full_name="Match", country_code="GB", currency_code="GBP")
    add_employee(session, full_name="Other country")
    add_employee(
        session,
        full_name="Other title",
        country_code="GB",
        currency_code="GBP",
        job_title="Staff Software Engineer",
    )

    response = client.get(
        "/api/employees",
        params={
            "country": "GB",
            "department": "Engineering",
            "job_title": "Senior Software Engineer",
        },
    )

    assert names(response) == ["Match"]


def test_searches_name_and_email_case_insensitively(client: TestClient, session: Session) -> None:
    add_employee(session, full_name="Priya Nair")
    add_employee(session, full_name="Someone Else", email="priya.contractor@acme-corp.com")
    add_employee(session, full_name="Unrelated")

    response = client.get("/api/employees", params={"q": "PRIYA"})

    assert names(response) == ["Priya Nair", "Someone Else"]


def test_search_treats_wildcards_literally(client: TestClient, session: Session) -> None:
    add_employee(session, full_name="Plain Name")

    response = client.get("/api/employees", params={"q": "%"})

    assert response.json()["total"] == 0


def test_hides_terminated_employees_unless_asked(client: TestClient, session: Session) -> None:
    add_employee(session, full_name="Current")
    add_employee(session, full_name="Leaver", status="terminated")

    assert names(client.get("/api/employees")) == ["Current"]
    assert names(client.get("/api/employees", params={"status": "terminated"})) == ["Leaver"]
    assert names(client.get("/api/employees", params={"status": "all"})) == ["Current", "Leaver"]


def test_rejects_unsupported_sort_and_oversized_pages(client: TestClient) -> None:
    response = client.get("/api/employees", params={"sort": "password", "page_size": 500})

    assert response.status_code == 422
    assert set(response.json()["error"]["fields"]) == {"sort", "page_size"}
