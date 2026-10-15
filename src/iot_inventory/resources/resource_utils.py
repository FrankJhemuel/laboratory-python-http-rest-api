import logging
import uuid

# Logger of the module (the name of the logger is the name of the module: iot_inventory.resources.resource_utils)
logger = logging.getLogger(__name__)


class ResourceUtils:
    """ Utility class with the helper methods shared by the Resources """

    @staticmethod
    def internal_server_error(operation: str) -> tuple[dict[str, str], int]:
        """
        Handle an unexpected exception raised while processing a request: log the error (with its stack trace)
        and build the 500 Internal Server Error response for the client.
        It must be called inside an 'except' block, so that the logger can access the exception being handled.
        """

        # Generate a unique identifier of the error to correlate the response received by the client
        # with the corresponding entry in the server log
        error_id = uuid.uuid4().hex

        # Log the error with the stack trace of the exception being handled (logger.exception uses the ERROR level)
        logger.exception("Internal Server Error [errorId: %s] while %s", error_id, operation)

        # The response does not contain the internal details of the exception (e.g., messages or stack trace),
        # which are written only in the server log, to avoid exposing implementation details to the clients
        return {'error': "Internal Server Error ! An unexpected error occurred while " + operation,
                'errorId': error_id}, 500
