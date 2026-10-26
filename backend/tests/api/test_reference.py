from fastapi.testclient import TestClient


def test_reference_lists_what_forms_and_filters_may_use(client: TestClient) -> None:
    body = client.get("/api/reference").json()

    assert {"code": "JP", "name": "Japan", "currency_code": "JPY"} in body["countries"]
    assert {"code": "JPY", "minor_unit": 0} in body["currencies"]
    assert body["departments"][0] == {
        "name": "Engineering",
        "job_titles": [
            "Software Engineer I",
            "Software Engineer II",
            "Senior Software Engineer",
            "Staff Software Engineer",
            "Principal Engineer",
            "Engineering Manager",
        ],
    }
    assert body["employment_types"] == ["full_time", "part_time", "contractor"]
    assert body["reporting_currency"] == "INR"
