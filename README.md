# Municipal Service Request Integration Demo

This is a small FastAPI demo for practising API design, data validation,
transformation, persistence, idempotency, error handling, and automated tests.

## Quick start

From the repository root, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the application and development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Start the API:

```powershell
python scripts\run_api.py
```

The runner prints the main URLs:

```text
API running at http://127.0.0.1:8000
Interactive docs at http://127.0.0.1:8000/docs
Health check at http://127.0.0.1:8000/health
```

Open this page in a browser to try the API:

```text
http://127.0.0.1:8000/docs
```

You can stop the API with `Ctrl+C`.

## Try a service request

In the Swagger UI at `/docs`, open:

```text
POST /api/v1/service-requests
```

Use this example payload:

```json
{
  "requestId": "REQ-DEMO-001",
  "customerId": "CUST-123",
  "serviceType": "broken_street_light",
  "description": "Street light is broken near the library",
  "priority": "high"
}
```

Then you can look up the stored integration run with:

```text
GET /api/v1/integration-runs/REQ-DEMO-001
```

## Reset demo data

For manual testing and automated runtime tests, the API includes a development
reset endpoint:

```text
DELETE /api/v1/admin/integration-data
```

This clears `integration_runs` and `dead_letters` from the local SQLite
database. It is meant for this local training demo, not as a production API
pattern.

## Run tests

Run the pytest suite:

```powershell
python -m pytest
```

Run the Robot Framework runtime API tests:

```powershell
python scripts\run_robot_tests.py
```

The Robot runner starts the API, waits for `/health`, runs the API tests,
clears demo data, and stops the API afterwards.

## Documentation

You can find the main documentation in the `docs` folder.

The documentation is divided into three main the areas listed below:

* [**architecture.md**](./docs/architecture.md) 
  This explains what problem this demo solves, how it solve it, which systems are involved and how are they connected, what the integration is responsible for, and what has been left out of scope.

* [**platform-mapping.md**](./docs/platform-mapping.md)
  This goes through how the integration thinking in this project could relate to concepts used in larger enterprise platforms.
  For example it tries to answer the question: "what would a larger corporation use instead of FastAPI?".

* [**ai-usage.md**](./docs/ai-usage.md)
  This contains a description of how AI was used in creating the project.
