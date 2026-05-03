import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

# Allow `python main.py` from this directory while keeping package-style imports.
from integration_demo.database import (  # noqa: E402
    clear_integration_data,
    initialize_database,
    get_integration_run_by_request_id,
)
from integration_demo.integration_service import process_service_request  # noqa: E402
from integration_demo.models import ServiceRequest  # noqa: E402

@asynccontextmanager
async def lifespan(_app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Municipal Service Request Integration Demo",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/v1/service-requests")
def create_service_request(request: ServiceRequest):
    try:
        result = process_service_request(request)
        return result
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/api/v1/integration-runs/{request_id}")
def get_integration_run(request_id: str):
    integration_run = get_integration_run_by_request_id(request_id)

    if integration_run is None:
        raise HTTPException(status_code=404, detail="Integration run not found")

    return integration_run


@app.delete("/api/v1/admin/integration-data")
def clear_integration_data_endpoint():
    clear_integration_data()
    return {"message": "Integration test data cleared"}
# Important note: this is an admin/testing endpoint. For a real production API, this would need authentication or an environment guard.


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
