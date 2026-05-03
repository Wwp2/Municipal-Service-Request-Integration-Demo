import json
import sqlite3
from datetime import datetime
from pathlib import Path

from integration_demo.models import IntegrationStatus


DATABASE_PATH = Path("integration_demo.db")


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS integration_runs (
                request_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                message TEXT NOT NULL,
                target_case_id TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS dead_letters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT,
                error_message TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def save_integration_run(
    request_id: str,
    status: IntegrationStatus,
    message: str,
    target_case_id: str | None = None,
):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO integration_runs
            (request_id, status, message, target_case_id, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                request_id,
                status.value,
                message,
                target_case_id,
                datetime.utcnow().isoformat(),
            ),
        )


def get_integration_run_by_request_id(request_id: str) -> dict | None:
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row

        row = connection.execute(
            """
            SELECT request_id, status, message, target_case_id, created_at
            FROM integration_runs
            WHERE request_id = ?
            """,
            (request_id,),
        ).fetchone()

    if row is None:
        return None

    return dict(row)


def save_dead_letter(
    request_id: str,
    error_message: str,
    payload: dict,
):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO dead_letters
            (request_id, error_message, payload, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                request_id,
                error_message,
                json.dumps(payload),
                datetime.utcnow().isoformat(),
            ),
        )