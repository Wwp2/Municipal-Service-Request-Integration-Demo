import sqlite3

from integration_demo import database
from integration_demo.integration_service import process_service_request
from integration_demo.models import IntegrationStatus, ServiceRequest


def test_process_service_request_returns_success_for_new_valid_request(
    temporary_database_path,
    valid_service_request,
):
    database.initialize_database()

    result = process_service_request(valid_service_request)

    integration_run = database.get_integration_run_by_request_id(
        valid_service_request.request_id
    )
    assert result.status == IntegrationStatus.SUCCESS
    assert result.target_case_id.startswith("CASE-")
    assert integration_run["status"] == "SUCCESS"
    assert integration_run["target_case_id"] == result.target_case_id


def test_process_service_request_returns_duplicate_when_request_was_already_processed(
    temporary_database_path,
    valid_service_request,
):
    database.initialize_database()
    database.save_integration_run(
        request_id=valid_service_request.request_id,
        status=IntegrationStatus.SUCCESS,
        message="Already processed",
        target_case_id="CASE-EXISTING",
    )

    result = process_service_request(valid_service_request)

    assert result.status == IntegrationStatus.DUPLICATE
    assert result.message == "This request has already been processed"
    assert result.target_case_id == "CASE-EXISTING"


def test_process_service_request_returns_failed_when_customer_cannot_be_found(
    temporary_database_path,
    valid_service_request_payload,
):
    database.initialize_database()
    valid_service_request_payload["customerId"] = "CUST-MISSING"
    request = ServiceRequest(**valid_service_request_payload)

    result = process_service_request(request)

    integration_run = database.get_integration_run_by_request_id(request.request_id)
    assert result.status == IntegrationStatus.FAILED
    assert result.message == "Customer not found: CUST-MISSING"
    assert integration_run["status"] == "FAILED"


def test_process_service_request_writes_dead_letter_when_processing_fails(
    temporary_database_path,
    valid_service_request_payload,
):
    database.initialize_database()
    valid_service_request_payload["requestId"] = "REQ-FAIL"
    request = ServiceRequest(**valid_service_request_payload)

    result = process_service_request(request)

    with sqlite3.connect(temporary_database_path) as connection:
        dead_letter_count = connection.execute(
            "SELECT COUNT(*) FROM dead_letters WHERE request_id = ?",
            ("REQ-FAIL",),
        ).fetchone()[0]

    assert result.status == IntegrationStatus.FAILED
    assert result.message == "Target system rejected the case"
    assert dead_letter_count == 1
