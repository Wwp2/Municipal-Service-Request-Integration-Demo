*** Settings ***
Library    Collections
Library    RequestsLibrary

Suite Setup       Create API Session And Reset Data
Suite Teardown    Reset Integration Data
Test Teardown     Reset Integration Data


*** Variables ***
${BASE_URL}    http://127.0.0.1:8000
${SERVICE_REQUEST_ENDPOINT}    /api/v1/service-requests
${INTEGRATION_RUN_ENDPOINT}    /api/v1/integration-runs
${RESET_ENDPOINT}    /api/v1/admin/integration-data


*** Test Cases ***
Health Endpoint Returns Ok Status
    ${response}=    GET On Session    api    /health    expected_status=200
    ${body}=    Set Variable    ${response.json()}
    Should Be Equal    ${body}[status]    ok

Create Valid Service Request Returns Success Result
    ${payload}=    Create Valid Service Request Payload    ROBOT-SUCCESS-001
    ${response}=    Create Service Request    ${payload}
    ${body}=    Set Variable    ${response.json()}
    Should Be Equal    ${body}[request_id]    ROBOT-SUCCESS-001
    Should Be Equal    ${body}[status]    SUCCESS
    Should Match Regexp    ${body}[target_case_id]    ^CASE-[A-F0-9]{8}$

Create Same Service Request Twice Returns Duplicate Result
    ${payload}=    Create Valid Service Request Payload    ROBOT-DUPLICATE-001
    ${first_response}=    Create Service Request    ${payload}
    ${second_response}=    Create Service Request    ${payload}
    ${first_body}=    Set Variable    ${first_response.json()}
    ${second_body}=    Set Variable    ${second_response.json()}
    Should Be Equal    ${first_body}[status]    SUCCESS
    Should Be Equal    ${second_body}[status]    DUPLICATE
    Should Be Equal    ${second_body}[target_case_id]    ${first_body}[target_case_id]

Invalid Service Request Returns Validation Error
    ${payload}=    Create Valid Service Request Payload    ROBOT-INVALID-001
    Set To Dictionary    ${payload}    description=Too short
    ${response}=    POST On Session
    ...    api
    ...    ${SERVICE_REQUEST_ENDPOINT}
    ...    json=${payload}
    ...    expected_status=422
    ${body}=    Set Variable    ${response.json()}
    Should Be True    isinstance($body["detail"], list)
    Should Be Equal    ${body}[detail][0][type]    string_too_short
    Should Be Equal    ${body}[detail][0][loc][0]    body
    Should Be Equal    ${body}[detail][0][loc][1]    description

Unknown Customer Returns Failed Integration Result
    ${payload}=    Create Valid Service Request Payload    ROBOT-MISSING-CUSTOMER-001
    Set To Dictionary    ${payload}    customerId=CUST-MISSING
    ${response}=    Create Service Request    ${payload}
    ${body}=    Set Variable    ${response.json()}
    Should Be Equal    ${body}[status]    FAILED
    Should Be Equal    ${body}[message]    Customer not found: CUST-MISSING
    Should Be Equal    ${body}[target_case_id]    ${None}

Target System Failure Returns Failed Integration Result
    ${payload}=    Create Valid Service Request Payload    REQ-FAIL
    ${response}=    Create Service Request    ${payload}
    ${body}=    Set Variable    ${response.json()}
    Should Be Equal    ${body}[request_id]    REQ-FAIL
    Should Be Equal    ${body}[status]    FAILED
    Should Be Equal    ${body}[message]    Target system rejected the case
    Should Be Equal    ${body}[target_case_id]    ${None}

Integration Run Can Be Fetched After Processing
    ${payload}=    Create Valid Service Request Payload    ROBOT-LOOKUP-001
    ${create_response}=    Create Service Request    ${payload}
    ${create_body}=    Set Variable    ${create_response.json()}
    ${lookup_response}=    GET On Session
    ...    api
    ...    ${INTEGRATION_RUN_ENDPOINT}/ROBOT-LOOKUP-001
    ...    expected_status=200
    ${lookup_body}=    Set Variable    ${lookup_response.json()}
    Should Be Equal    ${lookup_body}[request_id]    ROBOT-LOOKUP-001
    Should Be Equal    ${lookup_body}[status]    SUCCESS
    Should Be Equal    ${lookup_body}[target_case_id]    ${create_body}[target_case_id]

Failed Integration Run Can Be Fetched After Processing
    ${payload}=    Create Valid Service Request Payload    ROBOT-FAILED-LOOKUP-001
    Set To Dictionary    ${payload}    customerId=CUST-MISSING
    ${create_response}=    Create Service Request    ${payload}
    ${create_body}=    Set Variable    ${create_response.json()}
    ${lookup_response}=    GET On Session
    ...    api
    ...    ${INTEGRATION_RUN_ENDPOINT}/ROBOT-FAILED-LOOKUP-001
    ...    expected_status=200
    ${lookup_body}=    Set Variable    ${lookup_response.json()}
    Should Be Equal    ${create_body}[status]    FAILED
    Should Be Equal    ${lookup_body}[request_id]    ROBOT-FAILED-LOOKUP-001
    Should Be Equal    ${lookup_body}[status]    FAILED
    Should Be Equal    ${lookup_body}[message]    Customer not found: CUST-MISSING
    Should Be Equal    ${lookup_body}[target_case_id]    ${None}

Unknown Integration Run Returns Not Found
    ${response}=    GET On Session
    ...    api
    ...    ${INTEGRATION_RUN_ENDPOINT}/ROBOT-MISSING-001
    ...    expected_status=404
    ${body}=    Set Variable    ${response.json()}
    Should Be Equal    ${body}[detail]    Integration run not found


*** Keywords ***
Create API Session And Reset Data
    Create Session    api    ${BASE_URL}
    Reset Integration Data

Reset Integration Data
    DELETE On Session    api    ${RESET_ENDPOINT}    expected_status=200

Create Service Request
    [Arguments]    ${payload}
    ${response}=    POST On Session
    ...    api
    ...    ${SERVICE_REQUEST_ENDPOINT}
    ...    json=${payload}
    ...    expected_status=200
    RETURN    ${response}

Create Valid Service Request Payload
    [Arguments]    ${request_id}
    ${payload}=    Create Dictionary
    ...    requestId=${request_id}
    ...    customerId=CUST-123
    ...    serviceType=broken_street_light
    ...    description=Street light is broken near the library
    ...    priority=high
    RETURN    ${payload}
