from dataclasses import dataclass
from typing import Any
from iot_inventory.model.device_model import DeviceModel
from iot_inventory.dto.dto_utils import DtoUtils


@dataclass(frozen=True)
class DeviceUpdateRequest:
    """
    DTO representing the JSON body of the device update request (HTTP PUT /device/<device_id>).
    The uuid is not part of the body since the device is identified by the URL.
    """

    type: str
    softwareVersion: str
    manufacturer: str

    @classmethod
    def from_json(cls, data: Any) -> "DeviceUpdateRequest":
        """ Create the DTO from the deserialized JSON body (JSON -> DTO) """

        # The uuid identifies the device (through the URL) and cannot be changed: report a specific error
        # instead of the generic "Unknown fields" one to explain the problem to the client
        if isinstance(data, dict) and "uuid" in data:
            raise ValueError("Invalid device data ! The device uuid cannot be changed: "
                             "remove the uuid field from the body (the device is identified by the URL)")

        return cls(**DtoUtils.validate_fields(data, tuple(cls.__dataclass_fields__.keys())))

    def apply_to(self, device: DeviceModel) -> None:
        """ Update the editable fields of an existing DeviceModel (uuid and internal data are not changed) """
        device.device_type = self.type
        device.software_version = self.softwareVersion
        device.manufacturer = self.manufacturer
