import pytest

from integration_demo.mock_data import create_case_in_target_system, get_customer_by_id
from integration_demo.models import Priority, TargetCase


def test_get_customer_by_id_returns_customer_for_known_customer_id():
    customer = get_customer_by_id("CUST-123")

    assert customer is not None
    assert customer.id == "CUST-123"
    assert customer.name == "Example Person"


def test_get_customer_by_id_returns_none_for_unknown_customer_id():
    assert get_customer_by_id("CUST-999") is None


def test_create_case_in_target_system_returns_generated_case_id_for_valid_case():
    target_case = TargetCase(
        external_reference="REQ-123",
        case_type="INFRASTRUCTURE",
        title="Broken street light",
        description="Street light is broken near the library",
        customer_id="CUST-123",
        customer_name="Example Person",
        priority=Priority.HIGH,
        sla="2 business days",
    )

    target_case_id = create_case_in_target_system(target_case)

    assert target_case_id.startswith("CASE-")


def test_create_case_in_target_system_raises_error_for_rejected_case():
    target_case = TargetCase(
        external_reference="REQ-FAIL",
        case_type="INFRASTRUCTURE",
        title="Broken street light",
        description="Street light is broken near the library",
        customer_id="CUST-123",
        customer_name="Example Person",
        priority=Priority.HIGH,
        sla="2 business days",
    )

    with pytest.raises(RuntimeError, match="Target system rejected the case"):
        create_case_in_target_system(target_case)
