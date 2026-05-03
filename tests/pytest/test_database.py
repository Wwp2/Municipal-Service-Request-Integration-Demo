import json
import sqlite3
from datetime import datetime

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


def test_initialize_database_creates_expected_integration_run_columns(
    temporary_database_path,
):
    database.initialize_database()

    with sqlite3.connect(temporary_database_path) as connection:
        column_names = {
            row[1]
            for row in connection.execute("PRAGMA table_info(integration_runs)")
        }

    assert column_names == {
        "request_id",
        "status",
        "message",
        "target_case_id",
        "created_at",
    }


def test_initialize_database_creates_expected_dead_letter_columns(
    temporary_database_path,
):
    database.initialize_database()

    with sqlite3.connect(temporary_database_path) as connection:
        column_names = {
            row[1]
            for row in connection.execute("PRAGMA table_info(dead_letters)")
        }

    assert column_names == {
        "id",
        "request_id",
        "error_message",
        "payload",
        "created_at",
    }


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
    assert datetime.fromisoformat(integration_run["created_at"]).tzinfo is not None


def test_save_integration_run_replaces_existing_row_for_same_request_id(
    temporary_database_path,
):
    database.initialize_database()

    database.save_integration_run(
        request_id="REQ-123",
        status=IntegrationStatus.FAILED,
        message="Initial failure",
    )
    database.save_integration_run(
        request_id="REQ-123",
        status=IntegrationStatus.SUCCESS,
        message="Retry succeeded",
        target_case_id="CASE-RETRY",
    )

    with sqlite3.connect(temporary_database_path) as connection:
        row_count = connection.execute(
            "SELECT COUNT(*) FROM integration_runs WHERE request_id = ?",
            ("REQ-123",),
        ).fetchone()[0]

    integration_run = database.get_integration_run_by_request_id("REQ-123")
    assert row_count == 1
    assert integration_run["status"] == "SUCCESS"
    assert integration_run["message"] == "Retry succeeded"
    assert integration_run["target_case_id"] == "CASE-RETRY"


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
    assert datetime.fromisoformat(row[3]).tzinfo is not None


def test_clear_integration_data_removes_integration_runs_and_dead_letters(
    temporary_database_path,
):
    database.initialize_database()
    database.save_integration_run(
        request_id="REQ-123",
        status=IntegrationStatus.SUCCESS,
        message="Service request was successfully integrated",
        target_case_id="CASE-123",
    )
    database.save_dead_letter(
        request_id="REQ-FAIL",
        error_message="Target system rejected the case",
        payload={"requestId": "REQ-FAIL"},
    )

    database.clear_integration_data()

    with sqlite3.connect(temporary_database_path) as connection:
        integration_run_count = connection.execute(
            "SELECT COUNT(*) FROM integration_runs"
        ).fetchone()[0]
        dead_letter_count = connection.execute(
            "SELECT COUNT(*) FROM dead_letters"
        ).fetchone()[0]

    assert integration_run_count == 0
    assert dead_letter_count == 0
