import pytest

from integration_demo import database
from integration_demo.models import Customer, Priority, ServiceRequest, ServiceType


@pytest.fixture
def temporary_database_path(tmp_path, monkeypatch):
    database_path = tmp_path / "integration_demo_test.db"
    monkeypatch.setattr(database, "DATABASE_PATH", database_path)
    return database_path


@pytest.fixture
def valid_service_request():
    return ServiceRequest(
        requestId="REQ-123",
        customerId="CUST-123",
        serviceType=ServiceType.BROKEN_STREET_LIGHT,
        description="Street light is broken near the library",
        priority=Priority.HIGH,
    )


@pytest.fixture
def valid_service_request_payload():
    return {
        "requestId": "REQ-123",
        "customerId": "CUST-123",
        "serviceType": "broken_street_light",
        "description": "Street light is broken near the library",
        "priority": "high",
    }


@pytest.fixture
def valid_customer():
    return Customer(
        id="CUST-123",
        name="Example Person",
        email="example.person@example.com",
        municipality="Espoo",
    )
