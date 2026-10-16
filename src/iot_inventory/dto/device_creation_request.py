from dataclasses import dataclass
from typing import Any
from iot_inventory.model.device_model import DeviceModel
from iot_inventory.dto.dto_utils import DtoUtils


@dataclass(frozen=True)
class DeviceCreationRequest:
    """ DTO representing the JSON body of the device creation request (HTTP POST /device) """

    uuid: str
    type: str
    softwareVersion: str
    manufacturer: str

    @classmethod
    def from_json(cls, data: Any) -> "DeviceCreationRequest":
        """ Create the DTO from the deserialized JSON body (JSON -> DTO) """
        return cls(**DtoUtils.validate_fields(data, tuple(cls.__dataclass_fields__.keys())))

    def to_model(self) -> DeviceModel:
        """ Create a new DeviceModel from the DTO (DTO -> Model) """
        return DeviceModel(uuid=self.uuid,
                           device_type=self.type,
                           software_version=self.softwareVersion,
                           manufacturer=self.manufacturer)
