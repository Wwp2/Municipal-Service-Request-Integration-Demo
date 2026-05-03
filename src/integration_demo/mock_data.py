from uuid import uuid4

from integration_demo.models import Customer, TargetCase


CUSTOMERS = {
    "CUST-123": Customer(
        id="CUST-123",
        name="Example Person",
        email="example.person@example.com",
        municipality="Espoo",
    ),
    "CUST-456": Customer(
        id="CUST-456",
        name="Another Customer",
        email="another.customer@example.com",
        municipality="Helsinki",
    ),
}


def get_customer_by_id(customer_id: str) -> Customer | None:
    return CUSTOMERS.get(customer_id)


def create_case_in_target_system(target_case: TargetCase) -> str:
    """
    Simulates creating a case in an external case management system.

    Returns a generated target case id.
    """

    if target_case.external_reference == "REQ-FAIL":
        raise RuntimeError("Target system rejected the case")

    return f"CASE-{uuid4().hex[:8].upper()}"