# Platform mapping

## 1. Purpose of this document

This document describes how the concepts in this local Python/FastAPI/SQLite integration demo could map to common integration platform concepts.

The project itself is not implemented with Azure, MuleSoft, or Frends. Instead, it demonstrates integration fundamentals in a small local application: API design, validation, transformation, orchestration, persistence, error handling, idempotency, and documentation.

The goal of this document is to connect the demo implementation to platform-level thinking without claiming production experience with these platforms.

## 2. Conceptual mapping overview

| Demo concept | Azure concept | MuleSoft concept | Frends concept |
|---|---|---|---|
| Incoming API endpoint | API Management or HTTP-triggered Azure Function | API endpoint / Experience API | HTTP Trigger |
| Integration orchestration | Azure Function, Container App, or Logic App | Mule flow / Process API | Frends Process |
| Customer lookup | HTTP call to backend service or database | System API or connector call | Task calling an external system |
| Data transformation | Function code, mapping logic, or Logic Apps transformation | DataWeave transformation | Mapping logic inside a Process or Task |
| Target case creation | HTTP call, queue message, or backend connector | Connector call to target system | HTTP Task or connector Task |
| Integration run storage | Azure SQL, Table Storage, Cosmos DB, or Application logging | Object store, logging, or platform monitoring | Process execution history and logging |
| Dead letter handling | Service Bus dead-letter queue or error storage | Error handler / error routing | Process error handling / monitoring |
| Idempotency | Database constraint, request id tracking, Service Bus duplicate detection, or distributed state | Flow logic, object store, or idempotent consumer pattern | Process logic with stored request identifiers |
| Monitoring | Azure Monitor / Application Insights | Anypoint Monitoring / Visualizer | Frends monitoring dashboard |

## 3. Azure mapping

In an Azure-based version of this demo, the incoming API could be exposed through Azure API Management or an HTTP-triggered compute component such as Azure Functions.

The integration orchestration could be implemented with Azure Functions, Container Apps, or Logic Apps depending on the requirements. The customer lookup and target case creation would likely be implemented as HTTP calls, connector calls, or messages passed through Azure services.

For asynchronous or more resilient processing, Azure Service Bus could be used between the source system and the integration logic. Failed messages could be routed to a dead-letter queue for later inspection and reprocessing.

The local SQLite database in this demo could be replaced with a cloud persistence option such as Azure SQL, Table Storage, or Cosmos DB depending on requirements. Monitoring and diagnostics would likely be handled with Azure Monitor and Application Insights.

## 4. MuleSoft mapping

In a MuleSoft-based version, the integration could be modeled as an API-led flow.

One possible conceptual split would be:

| Layer | Possible responsibility |
|---|---|
| Experience API | Receives service requests from the source system |
| Process API | Orchestrates validation, customer lookup, transformation, and target case creation |
| System API | Provides access to customer data and the case management system |

The transformation from `ServiceRequest` and `Customer` into `TargetCase` could conceptually be implemented with MuleSoft transformation logic such as DataWeave.

Error handling could be implemented with Mule error handlers. For example, customer lookup errors, target system errors, and unexpected processing errors could be routed through defined error paths and logged or sent to an operational process for investigation.

## 5. Frends mapping

In a Frends-based version, the integration could be modeled as a Process started by an HTTP Trigger.

A simplified Frends-style flow could look like this:

| Demo step | Frends-style concept |
|---|---|
| Receive service request | HTTP Trigger |
| Validate request | Process logic or validation Task |
| Check duplicate request id | Task querying stored integration run data |
| Look up customer | Task calling a customer system |
| Transform request to target case | Mapping logic inside the Process |
| Create target case | HTTP Task or connector Task |
| Store integration result | Task writing to persistence or platform logging |
| Handle failure | Error handling path, Throw/Catch logic, monitoring |

The mock systems in this demo represent external dependencies that would normally be configured as real system calls or connectors in Frends.

## 6. What this project does not claim

This project does not claim to be a production-ready integration platform implementation.

It does not include:

- real Azure, MuleSoft, or Frends deployment
- production API security
- cloud infrastructure
- distributed message handling
- production monitoring
- real external system credentials or connectors
- high availability or scaling configuration

The purpose is to demonstrate understanding of integration concepts in a small, inspectable learning project.

## 7. Platform-specific next learning steps

Based on this demo, the next useful learning areas would be:

| Topic | Why it matters |
|---|---|
| API gateway concepts | To understand security, routing, throttling, and API lifecycle management |
| Message queues and dead-letter queues | To understand more resilient asynchronous integration patterns |
| OAuth2 and API authentication | To understand secure system-to-system communication |
| Platform monitoring | To understand how production integrations are observed and debugged |
| Hands-on Frends or MuleSoft tutorial | To connect the Python demo concepts to a real integration platform |
| Azure Functions and Service Bus | To learn how a similar integration could be implemented in Azure |