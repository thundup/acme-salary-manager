"""Time the API's main read paths against the database in DATABASE_URL.

Usage: DATABASE_URL=... uv run python -m app.bench [runs]
"""

import statistics
import sys
import time

from fastapi.testclient import TestClient

from app.main import create_app

REQUESTS = {
    "list, default page": "/api/employees",
    "list, page 300": "/api/employees?page=300",
    "list, country + sort by salary": "/api/employees?country=IN&sort=salary_minor&order=desc",
    "list, department + title": (
        "/api/employees?department=Engineering&job_title=Senior%20Software%20Engineer"
    ),
    "list, search 'sharma'": "/api/employees?q=sharma",
    "insights, all countries": "/api/insights/countries",
    "insights, IN by job title": "/api/insights/countries/IN/breakdown?by=job_title",
    "insights, IN distribution": "/api/insights/countries/IN/distribution",
    "insights, org summary": "/api/insights/summary",
}


def main() -> None:
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    with TestClient(create_app()) as client:
        for label, path in REQUESTS.items():
            client.get(path).raise_for_status()
            timings = []
            for _ in range(runs):
                started = time.perf_counter()
                client.get(path).raise_for_status()
                timings.append((time.perf_counter() - started) * 1000)
            median = statistics.median(timings)
            p95 = sorted(timings)[int(runs * 0.95) - 1]
            print(f"{label:<34} median {median:6.1f} ms   p95 {p95:6.1f} ms")


if __name__ == "__main__":
    main()
