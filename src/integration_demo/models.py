from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ServiceType(str, Enum):
    BROKEN_STREET_LIGHT = "broken_street_light"
    SNOW_CLEARING = "snow_clearing"
    WASTE_MANAGEMENT = "waste_management"
    GENERAL_FEEDBACK = "general_feedback"


class IntegrationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    DUPLICATE = "DUPLICATE"


class ServiceRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    request_id: str = Field(alias="requestId", min_length=1)
    customer_id: str = Field(alias="customerId", min_length=1)
    service_type: ServiceType = Field(alias="serviceType")
    description: str = Field(min_length=10)
    priority: Priority = Priority.NORMAL


class Customer(BaseModel):
    id: str
    name: str
    email: str
    municipality: str


class TargetCase(BaseModel):
    external_reference: str
    case_type: str
    title: str
    description: str
    customer_id: str
    customer_name: str
    priority: Priority
    sla: str


class IntegrationResult(BaseModel):
    request_id: str
    status: IntegrationStatus
    message: str
    target_case_id: str | None = None