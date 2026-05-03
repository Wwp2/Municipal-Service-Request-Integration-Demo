from integration_demo.database import (
    get_integration_run_by_request_id,
    save_dead_letter,
    save_integration_run,
)
from integration_demo.mock_data import (
    create_case_in_target_system,
    get_customer_by_id,
)
from integration_demo.models import (
    IntegrationResult,
    IntegrationStatus,
    ServiceRequest,
)
from integration_demo.transformer import transform_service_request_to_case


def process_service_request(request: ServiceRequest) -> IntegrationResult:
    existing_run = get_integration_run_by_request_id(request.request_id)

    if existing_run is not None:
        return IntegrationResult(
            request_id=request.request_id,
            status=IntegrationStatus.DUPLICATE,
            message="This request has already been processed",
            target_case_id=existing_run.get("target_case_id"),
        )

    try:
        customer = get_customer_by_id(request.customer_id)

        if customer is None:
            raise ValueError(f"Customer not found: {request.customer_id}")

        target_case = transform_service_request_to_case(request, customer)

        target_case_id = create_case_in_target_system(target_case)

        save_integration_run(
            request_id=request.request_id,
            status=IntegrationStatus.SUCCESS,
            message="Service request was successfully integrated",
            target_case_id=target_case_id,
        )

        return IntegrationResult(
            request_id=request.request_id,
            status=IntegrationStatus.SUCCESS,
            message="Service request was successfully integrated",
            target_case_id=target_case_id,
        )

    except Exception as error:
        save_integration_run(
            request_id=request.request_id,
            status=IntegrationStatus.FAILED,
            message=str(error),
        )

        save_dead_letter(
            request_id=request.request_id,
            error_message=str(error),
            payload=request.model_dump(mode="json"),
        )

        return IntegrationResult(
            request_id=request.request_id,
            status=IntegrationStatus.FAILED,
            message=str(error),
            target_case_id=None,
        )