from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import add_employee


def test_country_insights_return_money_with_its_currency(
    client: TestClient, session: Session
) -> None:
    add_employee(session, country_code="JP", currency_code="JPY", salary_minor=9_000_000)

    response = client.get("/api/insights/countries")

    assert response.status_code == 200
    assert response.json() == [
        {
            "country_code": "JP",
            "country_name": "Japan",
            "currency_code": "JPY",
            "headcount": 1,
            "min": {"amount_minor": 9_000_000, "currency": "JPY"},
            "max": {"amount_minor": 9_000_000, "currency": "JPY"},
            "average": {"amount_minor": 9_000_000, "currency": "JPY"},
            "median": {"amount_minor": 9_000_000, "currency": "JPY"},
        }
    ]


def test_breakdown_requires_a_supported_grouping(client: TestClient) -> None:
    response = client.get("/api/insights/countries/IN/breakdown", params={"by": "salary"})

    assert response.status_code == 422
    assert "by" in response.json()["error"]["fields"]


def test_breakdown_of_an_unknown_country_is_a_404(client: TestClient) -> None:
    response = client.get("/api/insights/countries/FR/breakdown", params={"by": "job_title"})

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "country_not_found"


def test_distribution_returns_buckets(client: TestClient, session: Session) -> None:
    add_employee(session, salary_minor=100)
    add_employee(session, salary_minor=300)

    response = client.get("/api/insights/countries/IN/distribution", params={"buckets": 2})

    assert response.json() == {
        "country_code": "IN",
        "currency_code": "INR",
        "buckets": [
            {"lower_minor": 100, "upper_minor": 201, "count": 1},
            {"lower_minor": 201, "upper_minor": 301, "count": 1},
        ],
    }


def test_distribution_bucket_count_is_bounded(client: TestClient) -> None:
    response = client.get("/api/insights/countries/IN/distribution", params={"buckets": 500})

    assert response.status_code == 422


def test_summary_is_labelled_approximate_with_its_rate_date(
    client: TestClient, session: Session
) -> None:
    add_employee(session, country_code="US", currency_code="USD", salary_minor=100_00)

    body = client.get("/api/insights/summary").json()

    assert body["approximate"] is True
    assert body["rates_as_of"] == "2026-10-01"
    assert body["headcount"] == 1
    assert body["total_salary"] == {"amount_minor": 8_800_00, "currency": "INR"}
