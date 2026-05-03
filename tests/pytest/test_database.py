import json
import sqlite3

from integration_demo import database
from integration_demo.models import IntegrationStatus


def test_initialize_database_creates_integration_run_and_dead_letter_tables(
    temporary_database_path,
):
    database.initialize_database()

    with sqlite3.connect(temporary_database_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert "integration_runs" in table_names
    assert "dead_letters" in table_names


def test_save_integration_run_stores_status_message_and_target_case_id(
    temporary_database_path,
):
    database.initialize_database()

    database.save_integration_run(
        request_id="REQ-123",
        status=IntegrationStatus.SUCCESS,
        message="Service request was successfully integrated",
        target_case_id="CASE-123",
    )

    integration_run = database.get_integration_run_by_request_id("REQ-123")

    assert integration_run["request_id"] == "REQ-123"
    assert integration_run["status"] == "SUCCESS"
    assert integration_run["message"] == "Service request was successfully integrated"
    assert integration_run["target_case_id"] == "CASE-123"
    assert integration_run["created_at"]


def test_get_integration_run_by_request_id_returns_none_for_missing_request_id(
    temporary_database_path,
):
    database.initialize_database()

    integration_run = database.get_integration_run_by_request_id("REQ-MISSING")

    assert integration_run is None


def test_save_dead_letter_stores_error_message_and_payload(temporary_database_path):
    database.initialize_database()

    database.save_dead_letter(
        request_id="REQ-FAIL",
        error_message="Target system rejected the case",
        payload={"requestId": "REQ-FAIL"},
    )

    with sqlite3.connect(temporary_database_path) as connection:
        row = connection.execute(
            """
            SELECT request_id, error_message, payload, created_at
            FROM dead_letters
            WHERE request_id = ?
            """,
            ("REQ-FAIL",),
        ).fetchone()

    assert row[0] == "REQ-FAIL"
    assert row[1] == "Target system rejected the case"
    assert json.loads(row[2]) == {"requestId": "REQ-FAIL"}
    assert row[3]
