from typing import Any


class DtoUtils:
    """ Utility class with the helper methods shared by the DTOs """

    @staticmethod
    def validate_fields(data: Any, fields: tuple[str, ...]) -> dict[str, str]:
        """
        Validate the deserialized JSON body against the expected fields of a DTO.
        The body must be a JSON object containing exactly the expected fields, all of them strings.
        Raise a ValueError (mapped to 400 Bad Request by the resources) describing the problem otherwise.
        """

        # The body must be a JSON object (e.g., not a list or null)
        if not isinstance(data, dict):
            raise ValueError("Invalid device data ! The body must be a JSON object")

        # All the expected fields must be present
        missing_fields = [field for field in fields if field not in data]
        if missing_fields:
            raise ValueError("Invalid device data ! Missing fields: " + ", ".join(missing_fields))

        # No other fields are allowed
        unknown_fields = [field for field in data if field not in fields]
        if unknown_fields:
            raise ValueError("Invalid device data ! Unknown fields: " + ", ".join(unknown_fields))

        # All the fields must be strings
        invalid_fields = [field for field in fields if not isinstance(data[field], str)]
        if invalid_fields:
            raise ValueError("Invalid device data ! Fields must be strings: " + ", ".join(invalid_fields))

        return data
