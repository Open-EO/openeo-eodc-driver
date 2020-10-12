"""Provide ResponseParser and APIException."""
import logging
from typing import Union
from uuid import uuid4

from flask import jsonify, make_response, redirect, request, send_file
from flask.wrappers import Response
from werkzeug.wrappers import Response as WerkzeugResponse


class APIException(Exception):
    """Returned if an Exception is raised in the gateway or one of the services.

    Attributes:
        msg: The error message.
        code: HTTP error code.
        service: Name of the service where the error occurred.
        user_id: The identifier of the user who triggered the error.
        internal: Flag an internal error.
        links: A list of links related to this error - currently not filled.
    """
    # TODO: links -> To exact Reference
    # TODO: links -> Retrieve own host name

    def __init__(self, msg: str = None, code: int = 500, service: str = None, user_id: str = None,
                 internal: bool = True, links: list = None) -> None:
        """Initialize APIExcepetion."""
        links = links if links else [""]
        self._id = uuid4()
        self._service = service
        self._user_id = user_id
        self._code = code
        self._msg = msg
        self._internal = internal
        self._links = [request.host_url + "redoc" + (link[1:] if link.startswith("/") else link) for link in links]

    def to_dict(self) -> dict:
        """Return a dict representation of the APIException object."""
        if self._msg:
            msg = self._msg
        elif self._internal:
            msg = "The request can't be fulfilled due to an error at the back-end."
        else:
            msg = "Something went wrong, but it's not clear what."
        return {
            "id": self._id,
            "code": self._code,
            "message": msg,
            "links": self._links,
            "service": self._service
        }

    def __str__(self) -> str:
        """Returns a string representation of the APIException object."""
        return "(code: {0}, service: {1}, uid: {2}) - Error {3}: {4}"\
               .format(self._code, self._service, self._user_id, self._id, self._msg)


class ResponseParser:
    """Responsible for generating and sending the response back to the user."""

    def __init__(self, logger: logging.Logger) -> None:
        """Initialize ResponseParser."""
        self._logger = logger

    def _code(self, code: int) -> Response:
        """Return a HTTP code response without a message.

        Args:
            code: The HTTP code.

        Returns:
            The Response object
        """
        return make_response("", code)

    def _string(self, code: int, msg: str) -> Response:
        """Return a message response back to the user.

        Args:
            code: The HTTP code.
            msg: The message.

        Returns:
            The Response object.
        """
        return make_response(str(msg), code)

    def _data(self, code: int, data: dict) -> Response:
        """Return a JSON response back to the user.

        Args:
            code: The HTTP code.
            data: The data to be parsed as JSON.

        Returns:
            The Response object.
        """
        return make_response(jsonify(data), code)

    def _html(self, file_name: str) -> Response:
        """Return a HTML page back to the user.

        The HTML file needs to be in the '/html' folder.

        Args:
            file_name: The file name of the HTML file.

        Returns:
            The Response object.
        """
        return send_file("html/" + file_name)

    def _file(self, filepath: str) -> Response:
        """Return a file back to the user.

        Args:
            filepath: The absolute filepath of the file requested by the user.

        Returns:
            The Response object.
        """
        return send_file(filepath)

    def parse(self, payload: dict) -> Response:
        """Map and parse the responses that are returned from the single endpoints.

        Args:
            payload: The payload object returned by the endpoints.

        Returns:
            The parsed response.
        """
        if "html" in payload:
            response = self._html(payload["html"])
        elif "msg" in payload:
            response = self._string(payload["code"], payload["msg"])
        elif "data" in payload:
            response = self._data(payload["code"], payload["data"])
        elif "file" in payload:
            response = self._file(payload["file"])
        else:
            response = self._code(payload["code"])

        if "headers" in payload:
            for h_key, h_val in payload["headers"].items():
                if h_key == "Location":
                    h_val = request.host_url + h_val
                response.headers[h_key] = h_val

        return response

    def error(self, exc: Union[dict, Exception]) -> Response:
        """Return an error response back to the user.

        The input can be either be a dict response of a service, an APIExcption object or a general Exception object.
        The error is logged using standard Flask logging.

        Args:
            exc: The input exception to return to the user.

        Returns:
            The Response object.
        """
        if isinstance(exc, dict):
            error = APIException(**exc)
        elif isinstance(exc, APIException):
            error = exc
        else:
            error = APIException(str(exc))

        self._logger.error(str(error))
        error_dict = error.to_dict()

        return make_response(jsonify(error_dict), error_dict["code"])

    def redirect_to(self, url: str) -> WerkzeugResponse:
        """Redirect to another URL.

        Args:
            url: The URL to redirect to.

        Returns:
            The Response object.
        """
        return redirect(url, code=300)
