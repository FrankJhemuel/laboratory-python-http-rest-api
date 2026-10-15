from datetime import datetime, timezone

class DeviceModel:
    """ Device Model Class: internal representation of a device used by the server (it does not know anything about JSON) """

    def __init__(self, uuid: str, device_type: str, software_version: str, manufacturer: str) -> None:
        self.uuid: str = uuid
        self.device_type: str = device_type
        self.software_version: str = software_version
        self.manufacturer: str = manufacturer

        # Internal data of the server: it is never exposed through the API representations (DTOs)
        self.created_at: datetime = datetime.now(timezone.utc)
