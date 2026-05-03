
* [**database.py**](src\integration_demo\database.py) creates the database management logic with SQLite and creates the main database for the system to store data.
This creates a integration_demo.db to store integration run history and failed messages.

* [**intergration_service.py**](src\integration_demo\intergration_service.py) contains the main intergration workflow for processing service requests.
It connects the database, mock customer data, transformer, and target system simulation together.
It handles successful requests, duplicate requests, and failed requests, and returns an IntegrationResult for the API response.

* [**main.py**](src\integration_demo\main.py) contains the FastApi application and defines all of the API endpoints used by the system.
It is also responsible for launching the app and keeping it running with uvicorn.

* [**mock_data.py**](src\integration_demo\mock_data.py) contains mock customer data and helper functions that simulate an external customer case management system.
In a real scenario this could be replaced with proper api calls to another system.

* [**models.py**](src\integration_demo\models.py) contains the shared Pydantic models used throughout the system.
These models define the expected format of servide requests, customers and target cases.

* [**transformer.py**](src\integration_demo\transformer.py) takes the service request data and customer data, and transforms it in to the case format the external target system expects.



### Development stack explanation and reasoning:

* **FastApi** was used as a fast and easy way to setup API:s for this application.

* **Pydantic** was used to help with data validation and serialisation in order to make communication with api:s safer and easier.
It was also useful in creating the main api documentation since you can automatically get the proper endpoint request and response formats out of it when used with FastApi.

* **SQLite** is used as a serverless database manager.