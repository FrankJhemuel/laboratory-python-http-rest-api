from typing import Any
from flask import request, Response
from flask_restful import Resource
from werkzeug.exceptions import BadRequest
from iot_inventory.dto.device_response import DeviceResponse
from iot_inventory.dto.device_update_request import DeviceUpdateRequest
from iot_inventory.persistence.data_manager import DataManager
from iot_inventory.resources.resource_utils import ResourceUtils

class DeviceResource(Resource):
    """ Device Resource Class extends Resource from Flask-RESTful to implement the HTTP Methods and RESTful API """

    def __init__(self, **kwargs: Any) -> None:
        """ Constructor """

        # Read the data manager from the keyword arguments and store it in the instance variable
        self.dataManager: DataManager = kwargs['data_manager']

    def get(self, device_id: str) -> tuple[dict[str, str], int]:
        """ Handle HTTP GET Request for the Device Resource """
        try:
            # Check if the device exists in the data manager
            if device_id in self.dataManager.device_dictionary:
                device = self.dataManager.device_dictionary[device_id]

                # Return the device representation (Model -> DTO -> JSON) with HTTP status code 200
                return DeviceResponse.from_model(device).to_json(), 200
            else:
                return {'error': "Device Not Found !"}, 404
        except Exception:
            # Unexpected error: log it and return 500 Internal Server Error
            return ResourceUtils.internal_server_error("reading the device")

    def put(self, device_id: str) -> Response | tuple[dict[str, str], int]:
        """ Handle HTTP PUT Request for the Device Resource """
        try:
            # Check if the device exists in the data manager
            if device_id in self.dataManager.device_dictionary:
                # The boolean flag force the parsing of POST data as JSON irrespective of the mimetype
                json_data = request.get_json(force=True)

                # Create and validate the update request DTO from the JSON data (JSON -> DTO).
                # The DTO does not contain the uuid: the device to update is identified by the URL
                update_request = DeviceUpdateRequest.from_json(json_data)

                # Apply the changes to the existing model (DTO -> Model) and update it in the data manager
                device = self.dataManager.device_dictionary[device_id]
                update_request.apply_to(device)
                self.dataManager.update_device(device)

                # Return HTTP status code 204 (No Content)
                return Response(status=204)
            else:
                return {'error': "Device UUID not found"}, 404
        except BadRequest:
            # Flask does not raise a JSONDecodeError when the body is not valid JSON: request.get_json()
            # raises a Werkzeug BadRequest exception instead. It must be caught explicitly (and before the
            # generic Exception) otherwise a client error would be reported as a 500 Internal Server Error
            return {'error': "Invalid JSON ! Check the request"}, 400
        except ValueError as e:
            # DeviceUpdateRequest.from_json() raises a ValueError when the JSON body does not match the
            # DTO (not a JSON object, missing, unknown or non-string fields). This is an error in the client
            # request, so we return 400 Bad Request (with the reason) instead of 500
            return {'error': str(e)}, 400
        except Exception:
            # Unexpected error: log it and return 500 Internal Server Error
            return ResourceUtils.internal_server_error("updating the device")

    def delete(self, device_id: str) -> Response | tuple[dict[str, str], int]:
        """ Handle HTTP DELETE Request for the Device Resource """
        try:
            # Check if the device exists in the data manager
            if device_id in self.dataManager.device_dictionary:

                # Remove the device from the data manager
                self.dataManager.remove_device(device_id)

                # Return HTTP status code 204 (No Content)
                return Response(status=204)
            else:
                return {'error': "Device UUID not found"}, 404
        except Exception:
            # Unexpected error: log it and return 500 Internal Server Error
            return ResourceUtils.internal_server_error("deleting the device")
