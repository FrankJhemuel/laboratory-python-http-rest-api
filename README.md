# Python - Laboratory RESTful HTTP API

This project is associated with the HTTP RESTful API Laboratory and it is used to show how to implement
a REST API through the use of the Python programming language and the following dependencies:

- Flask: https://flask.palletsprojects.com/en/2.3.x/
- Flask RESTful: https://flask-restful.readthedocs.io/en/latest/index.html

APIs are exposed through a configurable port (7070) and accessible locally at: http://127.0.0.1:7070/api/iot/inventory

In order to have additional information have a look at the official laboratory documentation and the step-by-step tutorial.

Laboratory structure and main sections are:

- [API HTTP RESTful Specifications](#api-http-restful-specifications)
- [Project Creation & Dependencies](#project-creation--dependencies)
- [Project Structure](#project-structure)
- [Running the Project](#running-the-project)
- [Resource, Representation and Model](#resource-representation-and-model)
- [Model Classes](#model-classes)
- [Device Data Manager](#device-data-manager)
- [Data Transfer Objects (DTOs)](#data-transfer-objects-dtos)
- [Creation of the Devices Resource](#creation-of-the-devices-resource)
- [HTTP Service Creation](#http-service-creation)
- [Creation of the Device Resource](#creation-of-the-device-resource)
- [Creating a New Device (HTTP - POST)](#creating-a-new-device-http---post)
- [Implementation of PUT and DELETE](#implementation-of-put-and-delete)

## API HTTP RESTful Specifications

In the following subsections, the specifications of the HTTP RESTful API to be implemented are provided. 
The base PATH to be used for the API is `api/iot/inventory`. 

An example of a complete URL associated with the PATH and the demo resource to be modeled (device) is: http://127.0.0.1:7070/api/iot/inventory/device.

### Device Data Structure

The data structure (JSON representation) of the IoT Device resource exchanged with the clients should include the following fields
(note that this is the **API contract** and it is not necessarily equal to the internal model of the server, 
see [Resource, Representation and Model](#resource-representation-and-model)):

- uuid (String): Unique identifier of the device. This ID will also be used as the key to identify it within the REST resources.
- type (String): Identifies the device type. Any value is allowed (e.g., temperature, humidity, demo sensor).
- softwareVersion (String): Represents the version of the software running on the device.
- manufacturer (String): Identifies the manufacturer of the device.

An example JSON representation of the resource to be modeled is as follows:

```json
{
    "uuid": "device00002",
    "type": "iot:demosensor",
    "softwareVersion": "v0.0.0.1",
    "manufacturer": "Acme-Inc"
}
```

### Endpoint HTTP RESTful to Design and Implement

For the device resource, the following endpoints are considered, 
along with their characteristics in terms of HTTP methods, body, headers, and response codes:

- **(READ DEVICE LIST) HTTP GET /device**: Returns the list of all devices registered on the server.
- Request Body: Empty
- Response:
  - Header: Content-Type: application/json
  - Body: [{…}, {…}, {Device Data Structure}]
  - Response Codes:
    - 200 OK
    - 400 Bad Request
    - 404 Not Found
    - 500 Internal Server Error

- **(CREATE NEW DEVICE) HTTP POST /device**: Create a new device.
- Request Body: {Device Data Structure}
- Response:
  - Header: Location: http://127.0.0.1:7070/api/iot/inventory/device/device00001
  - Body: Empty
  - Response Codes:
    - 201 Created
    - 400 Bad Request
    - 409 Conflict
    - 500 Internal Server Error

- **(READ DEVICE) HTTP GET /device/<device_id>**: Read the target device through its ID.
- Request Body: Empty
- Response:
  - Header: Content-Type: application/json
  - Body: {Device Data Structure}
  - Response Codes:
    - 200 OK
    - 400 Bad Request
    - 404 Not Found
    - 500 Internal Server Error

- **(UPDATE DEVICE) HTTP PUT /device/<device_id>**: Update a target device through its ID.
- Request Body: {Device Data Structure} without the `uuid` field (the device is identified by the `<device_id>` in the URL), e.g.:
  `{"type": "iot:demosensor", "softwareVersion": "v0.0.0.2", "manufacturer": "Acme-Inc"}`
- Response:
  - Body: Empty
  - Response Codes:
    - 204 No Content
    - 400 Bad Request (also when the body contains the `uuid`, since the UUID of a device cannot be changed)
    - 404 Not Found
    - 500 Internal Server Error

- **(REMOVE DEVICE) HTTP DELETE /device/<device_id>**: Delete the target device through its ID.
- Request Body: Empty
- Response:
  - Body: Empty
  - Response Codes:
    - 204 No Content
    - 400 Bad Request
    - 404 Not Found
    - 500 Internal Server Error

## Project Creation & Dependencies

The project uses the following dependencies:

- flask (Package Flask): Web Framework
- flask_restful (Package Flask-RESTful): Flask Plugin to build RESTful APIs

The project is managed with [uv](https://docs.astral.sh/uv/). Dependencies are declared in `pyproject.toml`,
locked in `uv.lock`, and the Python version (3.12) is pinned in `.python-version`.

Install uv (if needed) following the [official instructions](https://docs.astral.sh/uv/getting-started/installation/), e.g.:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then, from the project root, create the virtual environment (`.venv`) and install all the dependencies with:

```bash
uv sync
```

uv automatically downloads the required Python version if it is not available on your machine.
The command also installs the project itself (the `iot_inventory` package) in editable mode, 
so that the package can be imported and the `iot-inventory-server` command is available.

In PyCharm, you can select the existing `.venv` interpreter or add a new "uv" interpreter from the interpreter settings.
Mark the `src/` folder as **Sources Root** (right click on the folder → _Mark Directory as_ → _Sources Root_).

### Using pip (alternative)

The `requirements.txt` file is **generated** from `uv.lock` and is kept only for pip-based workflows:

```bash
pip install -r requirements.txt
```

The file also contains the line `-e .`, which installs the project itself in editable mode (as `uv sync` does).
Do not edit it manually. After changing the dependencies, regenerate it with:

```bash
uv export --no-hashes --no-dev -o requirements.txt
```

## Project Structure

The project follows the `src` layout: the server code is the `iot_inventory` package in `src/`.

```
laboratory-python-http-rest-api/
├── pyproject.toml              # Project metadata, dependencies and entry points
├── uv.lock                     # Locked dependency versions (managed by uv)
├── .python-version             # Pinned Python version (3.12)
├── requirements.txt            # Generated from uv.lock for pip users
├── images/                     # Images used in this README
└── src/iot_inventory/          # Server application package
    ├── __init__.py
    ├── __main__.py             # Enables: python -m iot_inventory
    ├── api_server.py           # create_server_app() factory and main() entry point
    ├── dto/
    │   ├── dto_utils.py                # DtoUtils class (helper methods shared by the DTOs)
    │   ├── device_creation_request.py  # DeviceCreationRequest class (POST body)
    │   ├── device_update_request.py    # DeviceUpdateRequest class (PUT body)
    │   └── device_response.py          # DeviceResponse class (GET response)
    ├── model/
    │   └── device_model.py     # DeviceModel class
    ├── persistence/
    │   └── data_manager.py     # DataManager class (in-memory storage)
    └── resources/
        ├── devices_resource.py # DevicesResource class (/device)
        └── device_resource.py  # DeviceResource class (/device/<device_id>)
```

- **Server Application** (`src/iot_inventory`):
  - _api_server.py_: The main entry point of the project. It contains:
    - `create_server_app()`: the Flask App Factory that creates the application and registers the API resources. If no Data Manager is passed, a new empty one is created. Importing the module has no side effects and each call returns a new, independent app (useful for testing with `app.test_client()`).
    - `load_demo_data()`: adds a demo device to the Data Manager.
    - `main()`: creates the Data Manager, loads the demo data, creates the app and starts the server on port 7070.
  - _\_\_main\_\_.py_: calls `main()` so that the server can also be started with `python -m iot_inventory`.
- **DTOs** (`dto/`):
  - Contains the Data Transfer Objects that describe the JSON representations exchanged with the clients, one class for each file: _device_creation_request.py_ (`DeviceCreationRequest`, POST body), _device_update_request.py_ (`DeviceUpdateRequest`, PUT body) and _device_response.py_ (`DeviceResponse`, GET response).
  - _dto_utils.py_: Contains the `DtoUtils` class with the static method `validate_fields()` used by the request DTOs to validate the JSON body.
- **Models** (`model/`):
  - _device_model.py_: Contains the `DeviceModel` class, the internal representation of an IoT device used by the server.
- **Persistence** (`persistence/`):
  - _data_manager.py_: Contains the `DataManager` class that stores the devices in memory (one independent dictionary for each `DataManager` instance).
- **Resources** (`resources/`):
  - _devices_resource.py_: Contains the `DevicesResource` class that handles the list of devices (`GET` and `POST` on `/device`).
  - _device_resource.py_: Contains the `DeviceResource` class that handles a single device (`GET`, `PUT` and `DELETE` on `/device/<device_id>`).

Each folder of the package contains an `__init__.py` file and internal modules are imported with 
absolute imports from the package, e.g.:

```python
from iot_inventory.model.device_model import DeviceModel
```

The project follows these code conventions:

- **One class for each file**: each class has a dedicated module named after the class in `snake_case` 
(e.g., `DeviceCreationRequest` in `device_creation_request.py`). In this way the structure of the folders mirrors 
the concepts of the project and each file has a single responsibility.
- **Helper logic in utility classes**: the logic shared by several classes is implemented as static methods of a 
dedicated utility class (e.g., `DtoUtils.validate_fields()` in `dto_utils.py`).
- **Type hints** on all parameters, return values and attributes (see [Model Classes](#model-classes)).

## Running the Project

The server is exposed as a command (`iot-inventory-server`) declared in the `[project.scripts]` section
of `pyproject.toml`. From the project root run:

```bash
uv run iot-inventory-server
```

Alternatively, you can run it as a module or execute the file directly:

```bash
uv run python -m iot_inventory
uv run src/iot_inventory/api_server.py
```

The server will start on all the network interfaces (`0.0.0.0`) and expose the API resources through the 
configured port by default (7070). Stop it with `CTRL+C`.

Since the app is built through the `create_server_app()` factory, it can also be started with the Flask CLI
(note that in this case the demo data are not loaded and, by default, the server listens only on `127.0.0.1`):

```bash
uv run flask --app "iot_inventory.api_server:create_server_app()" run --port 7070
```

With the server running, you can test the API with Postman (as shown in the following sections) or with `curl`, e.g.:

```bash
curl http://127.0.0.1:7070/api/iot/inventory/device
```

## Resource, Representation and Model

Before writing the code, it is important to distinguish four concepts that are often confused, 
since the same IoT device exists in different "forms", each one with a different responsibility:

| Concept | Where in the project | What it is |
|---|---|---|
| **REST Resource** | The URI `/device/<device_id>` | The abstract entity identified and addressed by the client |
| **Representation (DTO)** | `dto/` | The data exchanged on the wire (JSON): it is the **contract** of the API with its clients |
| **Model** | `model/` | The internal representation of the device used by the server (business logic and storage) |
| **Resource class (handler)** | `resources/` | The Flask-RESTful class that receives the HTTP request and coordinates DTOs, models and persistence |

A **DTO (Data Transfer Object)** is a simple object that contains only the data that are transferred between 
the client and the server in a specific interaction. Different interactions can have different representations 
of the same resource: in this project there is one DTO for the creation (POST), one for the update (PUT) and one 
for the reading (GET) of a device.

Keeping DTOs and models separate means that the internal model can evolve (e.g., renaming an attribute or adding 
internal data) without breaking the API contract used by the clients, and vice versa. 
To make this separation visible, in this project the model and the DTOs intentionally differ:

- **Naming**: the model follows the Python naming conventions (`device_type`, `software_version`), 
while the JSON representation keeps the camelCase names of the API contract (`type`, `softwareVersion`).
- **Internal data**: the model contains a `created_at` timestamp that is used only by the server and is never 
exposed through the API.
- **Different fields for different interactions**: the update DTO does not contain the `uuid`, 
since the device to be updated is identified by the URL.

The flow of the data through the layers is the following:

```
Write (POST/PUT):  JSON body --> DTO (validation) --> Model --> DataManager
Read  (GET):       DataManager --> Model --> DTO --> JSON body
```

## Model Classes

> **Note:** the following sections describe the step-by-step construction of the project. 
> All the files are created inside the `src/iot_inventory/` package (see [Project Structure](#project-structure)) 
> and the complete, commented implementation of each step is available in the repository.

Inside the package `src/iot_inventory/`, create a folder named `model` (with an empty `__init__.py` file). 
Inside it, create the file `device_model.py` and the following class `DeviceModel`, 
which will represent the internal description of our IoT object with the following fields:

- `uuid`: To uniquely identify the object.
- `device_type`: To specify the device type.
- `software_version`: For the version of software running on the device.
- `manufacturer`: To identify the device manufacturer.
- `created_at`: The creation timestamp of the object (internal data of the server, not exposed through the API).

The class example is provided in the following listing:

```python
from datetime import datetime, timezone

class DeviceModel:

    def __init__(self, uuid: str, device_type: str, software_version: str, manufacturer: str) -> None:
        self.uuid: str = uuid
        self.device_type: str = device_type
        self.software_version: str = software_version
        self.manufacturer: str = manufacturer
        self.created_at: datetime = datetime.now(timezone.utc)
```

Note that the model does not know anything about JSON and about the API: the conversion from and to the 
JSON representations is the responsibility of the DTOs (see [Data Transfer Objects (DTOs)](#data-transfer-objects-dtos)).

The code uses **type hints** (available since Python 3.5, with the modern syntax used here supported from Python 3.10):
the type of each parameter is written after its name (e.g., `uuid: str`), the return type after the arrow 
(e.g., `-> dict[str, str]`, or `-> None` when the method returns nothing) and the type of an attribute in its first assignment 
(e.g., `self.uuid: str = uuid`). Type hints are **not checked at runtime** by Python: they document the code, 
enable autocompletion and error highlighting in the IDE (e.g., PyCharm) and can be verified with static type checkers such as 
[mypy](https://mypy-lang.org/). Python 3.10+ also allows using built-in collections as generic types 
(e.g., `dict[str, DeviceModel]`, `list[dict[str, str]]`, `tuple[dict[str, str], int]`) and the `|` operator 
for union types (e.g., `DataManager | None`), which are used in the following sections.

## Device Data Manager

Inside the package `src/iot_inventory/`, create a new folder named `persistence` (with an empty `__init__.py` file)
which will contain the class for data storage (in this example, using a dictionary for in-memory storage). 
Within the persistence package, create the file `data_manager.py` with the following `DataManager` 
class responsible for handling all storage operations (create, update, and remove) for 
the project's devices using the previously created `DeviceModel` class:

```python
from iot_inventory.model.device_model import DeviceModel

class DataManager:

    def __init__(self) -> None:
        self.device_dictionary: dict[str, DeviceModel] = {}

    def add_device(self, new_device: DeviceModel) -> None:
        if isinstance(new_device, DeviceModel):
            self.device_dictionary[new_device.uuid] = new_device
        else:
            raise TypeError("Error adding new device ! Only DeviceModel are allowed !")

    def update_device(self, updated_device: DeviceModel) -> None:
        if isinstance(updated_device, DeviceModel):
            self.device_dictionary[updated_device.uuid] = updated_device
        else:
            raise TypeError("Error updating the device ! Only DeviceModel are allowed !")

    def remove_device(self, device_uuid: str) -> None:
        if device_uuid in self.device_dictionary.keys():
            del self.device_dictionary[device_uuid]
```

The `device_dictionary` (of type `dict[str, DeviceModel]`, i.e., a dictionary mapping each device UUID to its `DeviceModel`)
is created in the constructor (`__init__`) as an **instance attribute**: in this way each 
`DataManager` object has its own independent storage. Declaring it at class level (e.g., `device_dictionary = {}` 
directly in the class body) would instead create a single dictionary shared by all the instances of the class.

The methods within `DataManager` allow for creating, modifying, 
and removing devices from the dictionary and thus from the storage system. 
Specifically, note that the `add_device()` and `update_device()` 
methods validate the type of the parameter passed: the type hint `new_device: DeviceModel` documents the expected type, 
but since type hints are not enforced at runtime, the explicit check with `isinstance()` is still required. In the case of an invalid type different from `DeviceModel`, 
they raise a system exception of type `TypeError` to signal to the calling method the error with the provided parameter.

## Data Transfer Objects (DTOs)

Inside the package `src/iot_inventory/`, create a new folder named `dto` (with an empty `__init__.py` file) 
that will contain the DTOs of the device resource, **one class for each file**. 
Each DTO describes the JSON representation used in a specific interaction:

| Interaction | DTO (file) | JSON fields | Conversion |
|---|---|---|---|
| Creation (`POST /device`) | `DeviceCreationRequest` (`device_creation_request.py`) | uuid, type, softwareVersion, manufacturer | JSON → DTO → new Model |
| Update (`PUT /device/<device_id>`) | `DeviceUpdateRequest` (`device_update_request.py`) | type, softwareVersion, manufacturer | JSON → DTO → changes applied to the existing Model |
| Reading (`GET /device`, `GET /device/<device_id>`) | `DeviceResponse` (`device_response.py`) | uuid, type, softwareVersion, manufacturer | Model → DTO → JSON |

The DTOs are implemented as [dataclasses](https://docs.python.org/3/library/dataclasses.html): the `@dataclass` 
decorator automatically generates the constructor (and other methods) from the type-annotated fields, while 
`frozen=True` makes the objects immutable (a DTO is just a snapshot of the transferred data). 
The fields of the DTOs use the names of the API contract (e.g., `softwareVersion`), even if they do not follow 
the Python naming conventions, so that the JSON body can be converted into a DTO with `cls(**data)` and a DTO into 
a dictionary with `asdict(self)`. The `**` operator unpacks a dictionary into keyword arguments: 
`cls(**{"type": "a", "manufacturer": "b"})` is equivalent to `cls(type="a", manufacturer="b")`.

> **Note:** libraries such as [Pydantic](https://docs.pydantic.dev/) can automatically validate and convert DTOs. 
> In this laboratory we use only the standard library (`dataclasses`) on purpose: no additional dependencies are 
> required and the validation and the conversion between DTOs and models remain explicit and visible in the code.

### Validation of the Request Body

The two request DTOs share the same validation logic, implemented by the static method `validate_fields()` 
of the `DtoUtils` class, in the file `dto_utils.py`:

```python
from typing import Any


class DtoUtils:

    @staticmethod
    def validate_fields(data: Any, fields: tuple[str, ...]) -> dict[str, str]:
        if not isinstance(data, dict):
            raise ValueError("Invalid device data ! The body must be a JSON object")

        missing_fields = [field for field in fields if field not in data]
        if missing_fields:
            raise ValueError("Invalid device data ! Missing fields: " + ", ".join(missing_fields))

        unknown_fields = [field for field in data if field not in fields]
        if unknown_fields:
            raise ValueError("Invalid device data ! Unknown fields: " + ", ".join(unknown_fields))

        invalid_fields = [field for field in fields if not isinstance(data[field], str)]
        if invalid_fields:
            raise ValueError("Invalid device data ! Fields must be strings: " + ", ".join(invalid_fields))

        return data
```

The `@staticmethod` decorator defines a method that does not receive the instance (`self`) or the class (`cls`) 
as first parameter: it is called directly on the class (e.g., `DtoUtils.validate_fields(data, fields)`) without 
creating a `DtoUtils` object. The method checks that the deserialized JSON body is a JSON object containing exactly the expected 
fields, all of them strings. Otherwise, it raises a `ValueError` with a message describing the problem 
(e.g., `Missing fields: manufacturer`), which will be returned to the client with a `400 Bad Request` response.

### Creation Request DTO

Create the file `device_creation_request.py` with the `DeviceCreationRequest` class:

```python
from dataclasses import dataclass
from typing import Any
from iot_inventory.model.device_model import DeviceModel
from iot_inventory.dto.dto_utils import DtoUtils


@dataclass(frozen=True)
class DeviceCreationRequest:
    uuid: str
    type: str
    softwareVersion: str
    manufacturer: str

    @classmethod
    def from_json(cls, data: Any) -> "DeviceCreationRequest":
        return cls(**DtoUtils.validate_fields(data, ("uuid", "type", "softwareVersion", "manufacturer")))

    def to_model(self) -> DeviceModel:
        return DeviceModel(uuid=self.uuid,
                           device_type=self.type,
                           software_version=self.softwareVersion,
                           manufacturer=self.manufacturer)
```

- `from_json()` is a **class method** (`@classmethod`): it is called on the class (e.g., `DeviceCreationRequest.from_json(json_data)`) 
and receives the class itself as first parameter (`cls`) instead of an instance (`self`). It is used as an alternative 
constructor ("factory method"): `cls(...)` creates a new validated DTO from the JSON body. The return type is written as a string (`"DeviceCreationRequest"`) 
since the class is not fully defined yet while its body is being executed.
- `to_model()` creates a new `DeviceModel` from the creation request, mapping the names of the API contract 
to the names of the model (e.g., `softwareVersion` → `software_version`).

### Update Request DTO

Create the file `device_update_request.py` with the `DeviceUpdateRequest` class:

```python
from dataclasses import dataclass
from typing import Any
from iot_inventory.model.device_model import DeviceModel
from iot_inventory.dto.dto_utils import DtoUtils


@dataclass(frozen=True)
class DeviceUpdateRequest:
    type: str
    softwareVersion: str
    manufacturer: str

    @classmethod
    def from_json(cls, data: Any) -> "DeviceUpdateRequest":
        if isinstance(data, dict) and "uuid" in data:
            raise ValueError("Invalid device data ! The device uuid cannot be changed: "
                             "remove the uuid field from the body (the device is identified by the URL)")
        return cls(**DtoUtils.validate_fields(data, ("type", "softwareVersion", "manufacturer")))

    def apply_to(self, device: DeviceModel) -> None:
        device.device_type = self.type
        device.software_version = self.softwareVersion
        device.manufacturer = self.manufacturer
```

- The DTO does not contain the `uuid`, since the device to be updated is identified by the URL.
- `from_json()` explicitly rejects a body containing the `uuid` field: the `uuid` identifies 
the device (through the URL) and cannot be changed. A specific error message explains the problem to the client, 
instead of the generic `Unknown fields: uuid` that `DtoUtils.validate_fields()` would report.
- `apply_to()` updates only the editable fields of an existing `DeviceModel`: the `uuid` and the internal data 
(`created_at`) are not changed by the update.

### Response DTO

Create the file `device_response.py` with the `DeviceResponse` class:

```python
from dataclasses import dataclass, asdict
from iot_inventory.model.device_model import DeviceModel


@dataclass(frozen=True)
class DeviceResponse:
    uuid: str
    type: str
    softwareVersion: str
    manufacturer: str

    @classmethod
    def from_model(cls, device: DeviceModel) -> "DeviceResponse":
        return cls(uuid=device.uuid,
                   type=device.device_type,
                   softwareVersion=device.software_version,
                   manufacturer=device.manufacturer)

    def to_json(self) -> dict[str, str]:
        return asdict(self)
```

- `from_model()` and `to_json()` create the representation of a device to be returned to the client: 
note that `created_at` is not part of `DeviceResponse` and therefore it is never exposed.

The DTOs depend on the model (they know how to convert from and to `DeviceModel`), while the model does not 
depend on the DTOs: the internal representation does not know anything about how it is exposed through the API. 
In this project the conversion methods (`to_model()`, `apply_to()`, `from_model()`) are part of the DTOs to keep 
the code simple; in larger projects they are often moved to dedicated **mapper** classes.

## Creation of the Devices Resource

Inside the package `src/iot_inventory/`, create a new folder named `resources` (with an empty `__init__.py` file) 
that will contain the dedicated Python classes for describing the RESTful 
resources managed by the HTTP service. The Flask framework handles resources and their sub-elements differently. 
For this reason, it will be necessary to create separate classes for each type of resource. 
For example, to handle requests on `/device` and `/device/<device_id>`.

Firstly, let's begin with creating the class to handle requests on `/device` and enable the retrieval of the list of devices (GET) 
and their creation (POST).

Create a file named `devices_resource.py` containing the `DevicesResource` class with the following initial structure
(the imports of `request`, `Response`, `BadRequest` and `DeviceCreationRequest` will be used later to implement the `POST` method):

```python
from typing import Any
from flask import request, Response
from flask_restful import Resource
from werkzeug.exceptions import BadRequest
from iot_inventory.dto.device_creation_request import DeviceCreationRequest
from iot_inventory.dto.device_response import DeviceResponse
from iot_inventory.persistence.data_manager import DataManager

class DevicesResource(Resource):

    def __init__(self, **kwargs: Any) -> None:
        self.dataManager: DataManager = kwargs['data_manager']

    def get(self) -> tuple[list[dict[str, str]], int]:
        device_list: list[dict[str, str]] = []
        for device in self.dataManager.device_dictionary.values():
            device_list.append(DeviceResponse.from_model(device).to_json())
        return device_list, 200
```

The newly created class extends the Flask class Resource and has the following characteristics:

- The constructor allows retrieving variables passed during instantiation through a dictionary. In this specific case, we retrieve the `data_manager` variable of type `DataManager`, which will be stored as an attribute of the class (`self.dataManager: DataManager`) to maintain a reference for working with the stored data. The passing of `DataManager` to the class will be explained in the next step. Since `kwargs` can contain values of any type, it is annotated as `**kwargs: Any` (`Any` is imported from the standard `typing` module), while the type hint on `self.dataManager` tells the IDE and the type checker that it is a `DataManager`.
- The Flask framework, through the base class Resource, enables quick association of HTTP methods (GET, POST, PUT, DELETE) with Python functions named the same way (get, post, put, delete). In the current case, for instance, we can handle GET requests by redefining the method using the syntax: `def get(self):`. As illustrated later, these methods can also have parameters associated with the path and are usable within the function.
- The `get` method converts each `DeviceModel` stored in the `DataManager` into its representation through the `DeviceResponse` DTO (Model → DTO → JSON), instead of exposing the internal attributes of the model. It returns a tuple containing the response body (a list of dictionaries, one for each device, that Flask-RESTful serializes as JSON) and the HTTP status code. Its return type is therefore `tuple[list[dict[str, str]], int]`.

## HTTP Service Creation

Inside the package `src/iot_inventory/`, create a new file named `api_server.py` that will contain the definition of the HTTP server and its 
REST resources to be managed. The following listing presents the structure of the module:

```python
from flask import Flask
from flask_restful import Api
from iot_inventory.resources.devices_resource import DevicesResource
from iot_inventory.persistence.data_manager import DataManager
from iot_inventory.model.device_model import DeviceModel

ENDPOINT_PREFIX: str = "/api/iot/inventory"

DEFAULT_HOST: str = "0.0.0.0"
DEFAULT_PORT: int = 7070


def create_server_app(data_manager: DataManager | None = None) -> Flask:
    if data_manager is None:
        data_manager = DataManager()

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(DevicesResource, ENDPOINT_PREFIX + '/device',
                     resource_class_kwargs={'data_manager': data_manager},
                     endpoint="devices",
                     methods=['GET', 'POST'])

    return app


def load_demo_data(data_manager: DataManager) -> None:
    demo_device = DeviceModel("device00001", "iot:demosensor", "v0.0.0.1", "Acme-Inc")
    data_manager.add_device(demo_device)


def main() -> None:
    data_manager = DataManager()
    load_demo_data(data_manager)

    app = create_server_app(data_manager)

    print("Starting HTTP RESTful API Server ...")

    app.run(host=DEFAULT_HOST, port=DEFAULT_PORT)


if __name__ == '__main__':
    main()
```

In the provided code, the following aspects are highlighted:

- Imports necessary classes and references using absolute imports from the `iot_inventory` package.
- Defines the API endpoint prefix and the default host and port of the server as constants.
- `create_server_app()` implements the **App Factory** pattern:
  - Creates a Flask server and an API through Flask-RESTful using the statements `app = Flask(__name__)` and `api = Api(app)`. These variables are used to configure the REST resources and the server's operating parameters.
  - Receives the `DataManager` used to store the data (if it is not provided, a new empty one is created). The parameter is therefore annotated as `DataManager | None` with `None` as default value, and the function returns the created `Flask` app (`-> Flask`). This object is then passed to the resource classes for precise handling of data read and write functionalities.
  - Adds a new resource of the type `DevicesResource`, previously created and associated with the endpoint `/api/iot/inventory/device`, using the `api.add_resource` method. Additionally, it passes the `DataManager` reference to the resource through `resource_class_kwargs`, specifies an endpoint name, and defines the supported methods (Flask will automatically respond with a 405 Method Not Allowed for all other methods).
  - Returns the configured app without starting it.
- `load_demo_data()` creates a demo `DeviceModel` object and inserts it into the `DataManager` for testing purposes.
- `main()` is the entry point of the project: it creates the `DataManager`, loads the demo data, creates the app and starts the server 
on the port `7070` binding all the IPs and interfaces (specifying `0.0.0.0`).

Creating the app inside a function (instead of at module level) means that importing the module has no side effects 
(nothing is printed or created), each call to `create_server_app()` returns a new and independent app 
(e.g., to be used in tests through `app.test_client()`), and the app can also be started with the Flask CLI.

The project also contains the file `__main__.py` (which simply calls `main()` to enable `python -m iot_inventory`) and 
the following entry in `pyproject.toml`, which creates the `iot-inventory-server` command:

```toml
[project.scripts]
iot-inventory-server = "iot_inventory.api_server:main"
```

With the code defined above, you can launch the server (e.g., with `uv run iot-inventory-server`, see [Running the Project](#running-the-project)) 
and test the GET request to retrieve the list of registered devices using Postman. 
Once the service is launched, check the output in the console as shown in the following Figure.

![](images/run_log.png)

Subsequently, test the service using the Postman HTTP REST client with the following parameters:

- Method: GET 
- URL: http://127.0.0.1:7070/api/iot/inventory/device

The results on Postman are illustrated in the following Figure:

![](images/get_devices.png)

## Creation of the Device Resource

Inside the `resources` folder, create a file named `device_resource.py` containing the `DeviceResource` 
class to manage access to the resource associated with a single device, rather than a list of devices. 
The structure of the class is as follows (as before, the additional imports, including `DeviceUpdateRequest`, will be used later for the `PUT` method):

```python
from typing import Any
from flask import request, Response
from flask_restful import Resource
from werkzeug.exceptions import BadRequest
from iot_inventory.dto.device_response import DeviceResponse
from iot_inventory.dto.device_update_request import DeviceUpdateRequest
from iot_inventory.persistence.data_manager import DataManager

class DeviceResource(Resource):

    def __init__(self, **kwargs: Any) -> None:
        self.dataManager: DataManager = kwargs['data_manager']

    def get(self, device_id: str) -> tuple[dict[str, str], int]:
        if device_id in self.dataManager.device_dictionary:
            device = self.dataManager.device_dictionary[device_id]
            return DeviceResponse.from_model(device).to_json(), 200
        else:
            return {'error': "Device Not Found !"}, 404
```

The newly created class still extends the Flask class `Resource` 
but aims to handle requests arriving on paths of the form `/device/<device_id>`. 
The class possesses the following characteristics:

- The constructor allows retrieving variables passed during instantiation through a dictionary. 
In this specific case, we retrieve the `data_manager` variable of type `DataManager`, 
which will be stored as an attribute of the class to maintain a reference for working with the stored data.
- Definition of the method `def get(self, device_id: str) -> tuple[dict[str, str], int]:` to handle GET requests on the resource. 
As for the list of devices, the `DeviceModel` is converted into its `DeviceResponse` representation before being returned. 
In this case, there's an additional parameter that will be correctly passed by the Flask framework and will 
contain the value of the `device_id` passed in the path. For example, the value could be `device00001` with a URL structure like `http://127.0.0.1:7070/api/iot/inventory/device/device00001`

In order to test the service, it's necessary to first add the new resource and its management to the previously created 
`api_server.py` file. The code to be inserted consists of the correct reference 
import (`from iot_inventory.resources.device_resource import DeviceResource`) and then the following method call 
inside `create_server_app()`, after the registration of the `DevicesResource`:

```python
api.add_resource(DeviceResource, ENDPOINT_PREFIX + '/device/<string:device_id>',
                 resource_class_kwargs={'data_manager': data_manager},
                 endpoint='device',
                 methods=['GET', 'PUT', 'DELETE'])
```

The newly integrated code allows adding the new resource to the server and associating it with requests that match the specified 
path `/device/<string:device_id>`. 
The format `<string:device_id>` not only specifies the variable's key to use `device_id`, 
but also its type (in this case, `string` or, for example, `int`). 
As explained earlier, Flask will pass the value of the path parameter to the 
`get` method of the previously created `DeviceResource` class. 

Subsequently, test the service using the Postman HTTP REST client with the following parameters:

- Method: GET 
- URL: http://127.0.0.1:7070/api/iot/inventory/device/device00001

The results on Postman are illustrated in the following figure:

![](images/get_single_device.png)

## Creating a New Device (HTTP - POST)

In order to create a new device on the newly created server, it's necessary to handle the POST 
method in the `DevicesResource` class to respond appropriately to `POST` requests on the path `/device`. 
Specifically, add the following method to the `DevicesResource` class:

```python
def post(self) -> Response | tuple[dict[str, str], int]:
    try:
        json_data = request.get_json(force=True)
        creation_request = DeviceCreationRequest.from_json(json_data)
        if creation_request.uuid in self.dataManager.device_dictionary:
            return {'error': "Device UUID already exists"}, 409
        else:
            self.dataManager.add_device(creation_request.to_model())
            return Response(status=201, headers={"Location": request.url + "/" + creation_request.uuid})
    except BadRequest:
        return {'error': "Invalid JSON ! Check the request"}, 400
    except ValueError as e:
        return {'error': str(e)}, 400
    except Exception as e:
        return {'error': "Generic Internal Server Error ! Reason: " + str(e)}, 500
```

Specifically, the created code enables the following operations:

- Deserializes the received JSON body using the method `request.get_json(force=True)`, where the 
`request` object is provided by Flask (imported with `from flask import request`) and represents the current HTTP request. 
The use of the parameter `force=True` enforces deserialization even if the Content-Type specified 
by the client is not `application/json`. While the client should ideally always specify the correct type, 
forcing deserialization can help mitigate minor client errors.
- Transforms and validates the deserialized generic JSON object into the `DeviceCreationRequest` DTO using 
`DeviceCreationRequest.from_json(json_data)` (JSON → DTO).
- Checks if a device with the same `UUID` already exists in the `DataManager`. 
If so, it responds with an error message and a response code of `409 CONFLICT`.
- If the device is new, it creates the corresponding `DeviceModel` with `creation_request.to_model()` (DTO → Model), 
adds it to the `DataManager` and responds with a 
`201` response code and the `Location` header containing the URL to the new resource. 
In this case, the response uses the `Response` class to specify an empty body, 
which wouldn't be possible using the compact form `return <object>, <response_code>`.
So we use: `Response(status=201, headers={"Location": request.url + "/" + creation_request.uuid})`.
For this reason, the return type of the method is `Response | tuple[dict[str, str], int]`: 
either a `Response` object or a tuple with the error message and the status code.
- Handles client errors with a `400 Bad Request` response, catching the specific exceptions before the generic one 
(which is reported as `500 Internal Server Error`):
  - `BadRequest` (from `werkzeug.exceptions`): raised by `request.get_json()` when the body is not valid JSON. 
  Note that Flask does not raise a `JSONDecodeError` in this case, so catching `JSONDecodeError` would not work.
  - `ValueError`: raised by `DeviceCreationRequest.from_json()` when the body does not match the DTO 
  (missing, unknown or non-string fields) or when it is not a JSON object (e.g., a list or `null`). 
  The message of the exception, describing the problem, is returned to the client.

Use Postman to make a POST request with the following characteristics:

- Method: POST
- URL: http://127.0.0.1:7070/api/iot/inventory/device
- Body Type: RAW
- Format: JSON
- Body: As shown in the following listing and in Figure

```json
{
    "uuid": "device00002",
    "type": "iot:demosensor",
    "softwareVersion": "v0.0.0.1",
    "manufacturer": "Acme-Inc"
}
```

![](images/create_device.png)

Note in the Postman response how the response code is 201, there's no body present, 
and among the headers, the Location header contains the URL to which the client can 
make a new GET request to retrieve the representation of the created resource. 
Perform a test with a GET request to verify the proper functioning.

The same request can be executed with `curl`:

```bash
curl -i -X POST -H "Content-Type: application/json" \
     -d '{"uuid": "device00002", "type": "iot:demosensor", "softwareVersion": "v0.0.0.1", "manufacturer": "Acme-Inc"}' \
     http://127.0.0.1:7070/api/iot/inventory/device
```

## Implementation of PUT and DELETE

As additional exercises, implement and add the following methods to the `DeviceResource` class:

- `def put(...)` to be associated with the HTTP `PUT` method for updating an existing resource, 
performing appropriate checks on the request, resource ID, and body. The body must be converted into a 
`DeviceUpdateRequest` DTO (which does not contain the `uuid`, since the device is identified by the URL) and its 
changes applied to the existing `DeviceModel` with `apply_to()` (then save it with `update_device()` of the `DataManager`). 
As for the POST, catch the `ValueError` raised by `DeviceUpdateRequest.from_json()` to return its message to the client. In case of success, 
the response code should be `204` with no body, while in case of error, use `400` for an invalid request 
(invalid JSON, invalid device fields or an attempt to change the `uuid` by including it in the body), 
`404` for a resource not found or `500` in case of a server error. 
In all the error cases, specify a message in the body explaining the problem details.
- `def delete(...)` to be associated with the HTTP `DELETE` method for deleting a resource by its ID. 
In this case, it's necessary to validate and check the presence of the requested resource and respond with 
`204` with no body in case of success, `404` for a resource not found, or `500` in case of a server error. 
In both error cases, specify a message in the body explaining the problem details.

Below are the method declarations to be used: Flask-RESTful automatically associates them with the 
corresponding HTTP methods through their names. 
The student should fill in and complete these methods correctly to define their proper REST behavior.

```python
def put(self, device_id: str) -> Response | tuple[dict[str, str], int]:
    ... [TO BE COMPLETED] ...
```

```python
def delete(self, device_id: str) -> Response | tuple[dict[str, str], int]:
    ... [TO BE COMPLETED] ...
```

A reference solution is available in `src/iot_inventory/resources/device_resource.py`.

The implementation can be tested with Postman or with `curl`, e.g.:

```bash
# Update the device (204 No Content)
curl -i -X PUT -H "Content-Type: application/json" \
     -d '{"type": "iot:demosensor", "softwareVersion": "v0.0.0.2", "manufacturer": "Acme-Inc"}' \
     http://127.0.0.1:7070/api/iot/inventory/device/device00001

# Try to change the uuid (400 Bad Request: the device uuid cannot be changed)
curl -i -X PUT -H "Content-Type: application/json" \
     -d '{"uuid": "device99999", "type": "iot:demosensor", "softwareVersion": "v0.0.0.2", "manufacturer": "Acme-Inc"}' \
     http://127.0.0.1:7070/api/iot/inventory/device/device00001

# Delete the device (204 No Content) and read it again (404 Not Found)
curl -i -X DELETE http://127.0.0.1:7070/api/iot/inventory/device/device00001
curl -i http://127.0.0.1:7070/api/iot/inventory/device/device00001
```
