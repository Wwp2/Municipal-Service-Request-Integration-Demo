import pytest
from pydantic import ValidationError

from integration_demo.models import Priority, ServiceRequest, ServiceType


def test_service_request_accepts_valid_payload(valid_service_request_payload):
    request = ServiceRequest(**valid_service_request_payload)

    assert request.request_id == "REQ-123"
    assert request.customer_id == "CUST-123"
    assert request.service_type == ServiceType.BROKEN_STREET_LIGHT
    assert request.priority == Priority.HIGH


def test_service_request_uses_normal_priority_when_priority_is_not_provided(
    valid_service_request_payload,
):
    valid_service_request_payload.pop("priority")

    request = ServiceRequest(**valid_service_request_payload)

    assert request.priority == Priority.NORMAL


def test_service_request_rejects_payload_without_request_id(
    valid_service_request_payload,
):
    valid_service_request_payload.pop("requestId")

    with pytest.raises(ValidationError):
        ServiceRequest(**valid_service_request_payload)


def test_service_request_rejects_description_shorter_than_ten_characters(
    valid_service_request_payload,
):
    valid_service_request_payload["description"] = "Too short"

    with pytest.raises(ValidationError):
        ServiceRequest(**valid_service_request_payload)


def test_service_request_rejects_unknown_service_type(valid_service_request_payload):
    valid_service_request_payload["serviceType"] = "unknown_service_type"

    with pytest.raises(ValidationError):
        ServiceRequest(**valid_service_request_payload)
