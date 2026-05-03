from integration_demo.models import Priority, ServiceType
from integration_demo.transformer import (
    calculate_sla,
    transform_service_request_to_case,
)


def test_calculate_sla_returns_one_business_day_for_urgent_priority():
    assert calculate_sla("urgent") == "1 business day"


def test_calculate_sla_returns_two_business_days_for_high_priority():
    assert calculate_sla("high") == "2 business days"


def test_calculate_sla_returns_five_business_days_for_normal_priority():
    assert calculate_sla("normal") == "5 business days"


def test_calculate_sla_returns_ten_business_days_for_low_priority():
    assert calculate_sla("low") == "10 business days"


def test_transform_service_request_to_case_maps_request_and_customer_fields(
    valid_service_request,
    valid_customer,
):
    target_case = transform_service_request_to_case(
        valid_service_request,
        valid_customer,
    )

    assert target_case.external_reference == valid_service_request.request_id
    assert target_case.description == valid_service_request.description
    assert target_case.customer_id == valid_customer.id
    assert target_case.customer_name == valid_customer.name
    assert target_case.priority == Priority.HIGH


def test_transform_service_request_to_case_maps_service_type_to_case_details(
    valid_service_request,
    valid_customer,
):
    target_case = transform_service_request_to_case(
        valid_service_request,
        valid_customer,
    )

    assert valid_service_request.service_type == ServiceType.BROKEN_STREET_LIGHT
    assert target_case.case_type == "INFRASTRUCTURE"
    assert target_case.title == "Broken street light"
    assert target_case.sla == "2 business days"
