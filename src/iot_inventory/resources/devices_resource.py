from typing import Any
from flask import request, Response
from flask_restful import Resource
from werkzeug.exceptions import BadRequest
from iot_inventory.dto.device_creation_request import DeviceCreationRequest
from iot_inventory.dto.device_response import DeviceResponse
from iot_inventory.persistence.data_manager import DataManager
from iot_inventory.resources.resource_utils import ResourceUtils

class DevicesResource(Resource):
    """ Devices Resource Class extends Resource from Flask-RESTful to implement the HTTP Methods and RESTful API """

    def __init__(self, **kwargs: Any) -> None:
        """ Constructor """

        # Read the data manager from the keyword arguments and store it in the instance variable
        self.dataManager: DataManager = kwargs['data_manager']

    def get(self) -> tuple[list[dict[str, str]], int] | tuple[dict[str, str], int]:
        """ Handle HTTP GET Request for the Devices Resource """
        try:
            # Create a list of device representations from the devices stored in the data manager
            device_list: list[dict[str, str]] = []

            # Iterate over all devices stored in the data manager
            for device in self.dataManager.get_all_devices():
                # Convert each model to its response DTO (Model -> DTO) and then to a dictionary (DTO -> JSON)
                device_list.append(DeviceResponse.from_model(device).to_json())

            # Return the list of devices as JSON with HTTP status code 200
            return device_list, 200
        except Exception:
            # Unexpected error: log it and return 500 Internal Server Error
            return ResourceUtils.internal_server_error("reading the device list")

    def post(self) -> Response | tuple[dict[str, str], int]:
        """ Handle HTTP POST Request for the Devices Resource """

        try:
            # Read the JSON data from the request body. The boolean flag force the parsing of POST
            # data as JSON irrespective of the mimetype
            json_data = request.get_json(force=True)

            # Create and validate the creation request DTO from the JSON data (JSON -> DTO)
            creation_request = DeviceCreationRequest.from_json(json_data)

            # Check if the device UUID already exists in the data manager
            if self.dataManager.device_exists(creation_request.uuid):
                return {'error': "Device UUID already exists"}, 409
            else:
                # Create the model from the DTO (DTO -> Model) and add it to the data manager
                self.dataManager.add_device(creation_request.to_model())

                # Return HTTP status code 201 (Created) with the Location header pointing to the new resource
                return Response(status=201, headers={"Location": request.url + "/" + creation_request.uuid})
        except BadRequest:
            # Flask does not raise a JSONDecodeError when the body is not valid JSON: request.get_json()
            # raises a Werkzeug BadRequest exception instead. It must be caught explicitly (and before the
            # generic Exception) otherwise a client error would be reported as a 500 Internal Server Error
            return {'error': "Invalid JSON ! Check the request"}, 400
        except ValueError as e:
            # DeviceCreationRequest.from_json() raises a ValueError when the JSON body does not match the
            # DTO (not a JSON object, missing, unknown or non-string fields). This is an error in the client
            # request, so we return 400 Bad Request (with the reason) instead of 500
            return {'error': str(e)}, 400
        except Exception:
            # Unexpected error: log it and return 500 Internal Server Error
            return ResourceUtils.internal_server_error("creating the device")
