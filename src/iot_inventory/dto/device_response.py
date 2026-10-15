from dataclasses import dataclass, asdict
from iot_inventory.model.device_model import DeviceModel


@dataclass(frozen=True)
class DeviceResponse:
    """ DTO representing a device returned by the API (HTTP GET /device and /device/<device_id>) """

    uuid: str
    type: str
    softwareVersion: str
    manufacturer: str

    @classmethod
    def from_model(cls, device: DeviceModel) -> "DeviceResponse":
        """ Create the DTO from a DeviceModel (Model -> DTO) """
        return cls(uuid=device.uuid,
                   type=device.device_type,
                   softwareVersion=device.software_version,
                   manufacturer=device.manufacturer)

    def to_json(self) -> dict[str, str]:
        """ Convert the DTO to a dictionary that Flask-RESTful serializes as JSON (DTO -> JSON) """
        return asdict(self)
