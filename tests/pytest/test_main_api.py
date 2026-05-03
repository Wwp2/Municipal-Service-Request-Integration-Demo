from fastapi.testclient import TestClient

from integration_demo import database
from integration_demo.main import app
from integration_demo.models import IntegrationStatus


def test_health_endpoint_returns_ok_status(temporary_database_path):
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_service_request_endpoint_accepts_valid_payload(
    temporary_database_path,
    valid_service_request_payload,
):
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/service-requests",
            json=valid_service_request_payload,
        )

    response_body = response.json()
    assert response.status_code == 200
    assert response_body["request_id"] == "REQ-123"
    assert response_body["status"] == "SUCCESS"
    assert response_body["target_case_id"].startswith("CASE-")


def test_create_service_request_endpoint_returns_duplicate_for_repeated_request(
    temporary_database_path,
    valid_service_request_payload,
):
    with TestClient(app) as client:
        first_response = client.post(
            "/api/v1/service-requests",
            json=valid_service_request_payload,
        )
        second_response = client.post(
            "/api/v1/service-requests",
            json=valid_service_request_payload,
        )

    first_response_body = first_response.json()
    second_response_body = second_response.json()
    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response_body["status"] == "SUCCESS"
    assert second_response_body["status"] == "DUPLICATE"
    assert (
        second_response_body["target_case_id"]
        == first_response_body["target_case_id"]
    )


def test_create_service_request_endpoint_rejects_invalid_payload(
    temporary_database_path,
    valid_service_request_payload,
):
    valid_service_request_payload["description"] = "Too short"

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/service-requests",
            json=valid_service_request_payload,
        )

    assert response.status_code == 422


def test_get_integration_run_endpoint_returns_saved_integration_run(
    temporary_database_path,
):
    database.initialize_database()
    database.save_integration_run(
        request_id="REQ-LOOKUP",
        status=IntegrationStatus.SUCCESS,
        message="Service request was successfully integrated",
        target_case_id="CASE-LOOKUP",
    )

    with TestClient(app) as client:
        response = client.get("/api/v1/integration-runs/REQ-LOOKUP")

    response_body = response.json()
    assert response.status_code == 200
    assert response_body["request_id"] == "REQ-LOOKUP"
    assert response_body["status"] == "SUCCESS"
    assert response_body["target_case_id"] == "CASE-LOOKUP"


def test_get_integration_run_endpoint_returns_not_found_for_unknown_request_id(
    temporary_database_path,
):
    with TestClient(app) as client:
        response = client.get("/api/v1/integration-runs/REQ-MISSING")

    assert response.status_code == 404
    assert response.json() == {"detail": "Integration run not found"}


def test_clear_integration_data_endpoint_removes_saved_integration_data(
    temporary_database_path,
    valid_service_request_payload,
):
    with TestClient(app) as client:
        create_response = client.post(
            "/api/v1/service-requests",
            json=valid_service_request_payload,
        )
        clear_response = client.delete("/api/v1/admin/integration-data")
        lookup_response = client.get("/api/v1/integration-runs/REQ-123")

    assert create_response.status_code == 200
    assert clear_response.status_code == 200
    assert clear_response.json() == {"message": "Integration test data cleared"}
    assert lookup_response.status_code == 404
