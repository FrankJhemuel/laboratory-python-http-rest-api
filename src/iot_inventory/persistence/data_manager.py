from iot_inventory.model.device_model import DeviceModel

class DataManager:
    """ Data Manager Class """

    def __init__(self) -> None:
        """ Constructor """

        # Initialize the data manager with an empty dictionary to store the devices
        # (instance attribute: each DataManager has its own independent storage).
        # The leading underscore marks the attribute as private by convention: the other classes (e.g., the
        # Resources) must use the methods of the DataManager instead of accessing the dictionary directly,
        # so that the storage can be changed (e.g., with a database) without modifying them
        self._device_dictionary: dict[str, DeviceModel] = {}

    def get_device(self, device_uuid: str) -> DeviceModel | None:
        """
        Return the device with the given uuid, or None if it does not exist.

        Returning None (instead of raising an exception) is a design choice: a missing device is an expected
        situation (e.g., a client requesting a wrong uuid) and not an error of the DataManager, so the caller
        can check the result with a single lookup and decide the response (e.g., 200 OK or 404 Not Found).
        The alternatives are:
        - raising an exception (e.g., KeyError or a custom DeviceNotFoundError) that the caller must catch:
          useful when a missing device is really an unexpected error;
        - checking the existence first with device_exists() and then reading the device: it requires two
          lookups and the device could be removed between the two calls (in a concurrent server).
        """

        # dict.get() returns None when the key does not exist (instead of raising a KeyError like dict[key])
        return self._device_dictionary.get(device_uuid)

    def get_all_devices(self) -> list[DeviceModel]:
        """ Return the list of all the stored devices """

        # Return a new list (a copy): the caller cannot add or remove devices in the internal dictionary
        return list(self._device_dictionary.values())

    def device_exists(self, device_uuid: str) -> bool:
        """ Check if a device with the given uuid exists in the data manager """
        return device_uuid in self._device_dictionary

    def add_device(self, new_device: DeviceModel) -> None:
        """ Add a new device to the data manager """

        # Check if the new device is a DeviceModel
        if not isinstance(new_device, DeviceModel):
            raise TypeError("Error adding new device ! Only DeviceModel are allowed !")

        # Check if the device already exists, in order to avoid silently overwriting it
        if new_device.uuid in self._device_dictionary:
            raise ValueError("Error adding new device ! Device UUID already exists !")

        self._device_dictionary[new_device.uuid] = new_device

    def update_device(self, updated_device: DeviceModel) -> None:
        """ Update an existing device in the data manager """

        # Check if the updated device is a DeviceModel
        if not isinstance(updated_device, DeviceModel):
            raise TypeError("Error updating the device ! Only DeviceModel are allowed !")

        # Check if the device exists, in order to avoid adding a new device through an update
        if updated_device.uuid not in self._device_dictionary:
            raise KeyError("Error updating the device ! Device UUID not found !")

        self._device_dictionary[updated_device.uuid] = updated_device

    def remove_device(self, device_uuid: str) -> bool:
        """ Remove a device from the data manager. Return True if the device was removed, False if it does not exist """

        # Check if the device exists in the data manager
        if device_uuid in self._device_dictionary:
            del self._device_dictionary[device_uuid]
            return True
        else:
            return False
