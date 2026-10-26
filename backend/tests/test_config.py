import pytest

from app.config import Settings


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("postgres://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
        (
            "postgresql://u:p@host/db?sslmode=require",
            "postgresql+psycopg://u:p@host/db?sslmode=require",
        ),
        ("postgresql+psycopg://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
        ("sqlite:///./acme.db", "sqlite:///./acme.db"),
    ],
)
def test_database_urls_from_hosting_providers_use_the_psycopg_driver(
    given: str, expected: str
) -> None:
    assert Settings(database_url=given).database_url == expected
