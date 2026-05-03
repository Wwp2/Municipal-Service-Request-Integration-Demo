from integration_demo.models import (
    Customer,
    ServiceRequest,
    ServiceType,
    TargetCase,
)


SERVICE_TYPE_TO_CASE_TITLE = {
    ServiceType.BROKEN_STREET_LIGHT: "Broken street light",
    ServiceType.SNOW_CLEARING: "Snow clearing request",
    ServiceType.WASTE_MANAGEMENT: "Waste management issue",
    ServiceType.GENERAL_FEEDBACK: "General feedback",
}


SERVICE_TYPE_TO_CASE_TYPE = {
    ServiceType.BROKEN_STREET_LIGHT: "INFRASTRUCTURE",
    ServiceType.SNOW_CLEARING: "INFRASTRUCTURE",
    ServiceType.WASTE_MANAGEMENT: "ENVIRONMENT",
    ServiceType.GENERAL_FEEDBACK: "GENERAL",
}


def calculate_sla(priority: str) -> str:
    if priority == "urgent":
        return "1 business day"
    if priority == "high":
        return "2 business days"
    if priority == "normal":
        return "5 business days"

    return "10 business days"


def transform_service_request_to_case(
    request: ServiceRequest,
    customer: Customer,
) -> TargetCase:
    return TargetCase(
        external_reference=request.request_id,
        case_type=SERVICE_TYPE_TO_CASE_TYPE[request.service_type],
        title=SERVICE_TYPE_TO_CASE_TITLE[request.service_type],
        description=request.description,
        customer_id=customer.id,
        customer_name=customer.name,
        priority=request.priority,
        sla=calculate_sla(request.priority.value),
    )