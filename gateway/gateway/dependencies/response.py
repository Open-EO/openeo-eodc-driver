""" ResponseParser, APIException """

from flask import make_response, jsonify, send_file, request, redirect
from flask.wrappers import Response
from uuid import uuid4
from typing import Union


class APIException(Exception):
    """APIException if a Exception in the API gateway or one of the services raises
    or a HTTP error is send back by one of the services.
    """
    # TODO: links -> To exact Reference
    # TODO: links -> Rertrieve own host name

    def __init__(self, msg: str=None, code: int=500, service: str=None,
                 user_id: str=None, internal: bool=True, 
                 links: list=[""], **args):

        self._id = uuid4()
        self._service = service
        self._user_id = user_id
        self._code = code
        self._msg = msg
        self._internal = internal
        self._links = [request.host_url + "redoc" + (link[1:] if link.startswith("/") else link) for link in links]

    def to_dict(self):
        """Returns a dict representation of the APIException object.
        If the 
        """

        if self._internal:
            # TODO: Custom HTTP Code messages?
            msg = "The request can't be fulfilled due to an error at the back-end."
        else:
            msg = self._msg

        return {
            "id": self._id,
            "code": self._code,
            "message": msg,
            "links": self._links
        }

    def __str__(self):
        """Returns a string representation of the APIException object.
        """

        return "(code: {0}, service {1}, uid: {2}) {3}: {4}"\
               .format(self._code, self._service, self._user_id, self._id, self._msg)


class ResponseParser:
    """The ResponseParser is responsible for generating and sending the response back
    to the user. Furthermore, it is responsible for aggregated logging. 
    """

    def __init__(self, logger):
        self._logger = logger

    def code(self, code: int) -> Response:
        """Returns a HTTP code response without a message.

        Arguments:
            code {int} -- The HTTP code

        Returns:
            Response -- The Response object
        """

        return make_response("", code)

    def string(self, code: int, msg: str) -> Response:
        """Returns a message response back to the user.

        Arguments:
            code {int} -- The HTTP code
            msg {str} -- The message

        Returns:
            Response -- The Response object
        """

        return make_response(str(msg), code)

    def data(self, code: int, data: dict) -> Response:
        """Returns a JSON response back to the user.

        Arguments:
            code {int} -- The HTTP code
            data {dict} -- The data to be parsed as JSON

        Returns:
            Response -- The Response object
        """

        return make_response(jsonify(data), code)

    def html(self, file_name: str) -> Response:
        """Returns a HTML page back to the user. The HTML file needs to be in the
        '/html' folder.

        Arguments:
            file_name {str} -- The file name of the HTML file 

        Returns:
            Response -- The Response object
        """

        return send_file("html/" + file_name)

    def error(self, exc: Union[dict, Exception]) -> Response:
        """Returns a error response back to the user. The input can be either be a dict response
        of a service, a APIExcption object or a general Exception object. The error is logged 
        using standard Flask logging.

        Arguments:
            exc {Union[dict, Exception]} -- The input exception

        Returns:
            Response -- The Response object
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
    
    def redirect(self, url:str) -> Response:
        """Redirects to another URL
        
        Arguments:
            url {str} -- The URL to redirect to
        
        Returns:
            Response -- The Response object
        """

        return redirect(url, code=303)
