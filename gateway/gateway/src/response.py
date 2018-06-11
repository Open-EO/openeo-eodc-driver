from flask import make_response, jsonify
from .cors import response_headers
from uuid import uuid4
#TODO: Aggregated Logging


class OK:
    def __init__(self, msg):
        self.code = 200
        self.msg = msg

    def __parse__(self):
        return {
            "description": self.msg,
            "headers": response_headers
        }


class APIException(Exception):
    def __init__(self, code, msg, service, user_id):
        self.id = uuid4()
        self.service = service
        self.user_id = user_id
        self.code = code
        self.msg = msg
        self.out_msg = ""
        self.url = "http://www.openeo.org/tbd"

    def out(self):
        return {
            "id": self.id,
            "code": self.code,
            "message": self.msg,
            "url": self.url
        }
    
    def _log(self):
        print("{0} - {1}: {2}".format(self.user_id, self.service, self.msg))    # TODO: Logging

    def __str__(self):
        return self.out_msg

    def __parse__(self):
        return {"description": self.out_msg}


class BadRequest(APIException):
    def __init__(self, msg=None, service=None, user_id=None):
        super().__init__(400, msg, service, user_id)
        self.out_msg = msg if msg else "The server cannot or will not process the request due to an apparent client error."


class Unauthorized(APIException):
    def __init__(self, msg=None, service=None, user_id=None):
        super().__init__(401, msg, service, user_id)
        self.out_msg = self.out_msg = msg if msg else "The back-end requires clients to authenticate in order to process this request. Your account may not be activated."


class Forbidden(APIException):
    def __init__(self, msg=None, service=None, user_id=None):
        super().__init__(403, msg, service, user_id)
        self.out_msg = self.out_msg = msg if msg else "Authorization failed, access to the requested resource has been denied."


class NotFound(APIException):
    def __init__(self, msg=None, service=None, user_id=None):
        super().__init__(404, msg, service, user_id)
        self.out_msg = "The requested resource could not be found but may be available in the future."


class MethodNotAllowed(APIException):
    def __init__(self, msg=None, service=None, user_id=None):
        super().__init__(405, msg, service, user_id)
        self.out_msg = "The requested HTTP method is not supported or allowed to be requested."


class NotAcceptable(APIException):
    def __init__(self, msg=None, service=None, user_id=None):
        super().__init__(406, msg, service, user_id)
        self.out_msg = "The server is not capable to deliver the requested format."


class Conflict(APIException):
    def __init__(self, msg=None, service=None, user_id=None):
        super().__init__(409, msg, service, user_id)
        self.out_msg = "The request could not be processed because of conflict in the request. An entity with the same id might already exist."


class InternalServerError(APIException):
    def __init__(self, msg=None, service=None, user_id=None):
        super().__init__(500, msg, service, user_id)
        self.out_msg = "The request can't be fulfilled due to an error at the back-end."


class NotImplemented(APIException):
    def __init__(self, msg=None, service=None, user_id=None):
        super().__init__(501, msg, service, user_id)
        self.out_msg = "This API feature is not supported by the back-end."


class ServiceUnavailable(APIException):
    def __init__(self, msg=None, service=None, user_id=None):
        super().__init__(503, msg, service, user_id)
        self.out_msg = "The service is currently unavailable."


class ResponseParser:
    EXC_MAPPING = {
        "BadRequest": BadRequest,
        "Unauthorized": Unauthorized,
        "Forbidden": Forbidden,
        "NotFound": NotFound,
        "Conflict": Conflict,
        "MethodNotAllowed": MethodNotAllowed,
        "NotAcceptable": NotAcceptable,
        "InternalServerError": InternalServerError,
        "NotImplemented": NotImplemented,
        "ServiceUnavailable": ServiceUnavailable,
        "RpcTimeout": ServiceUnavailable,
        "IntegrityError": Conflict,
        "TypeError": InternalServerError
    }

    def code(self, code):
        return make_response("", code)

    def string(self, code, msg):
        return make_response(str(msg), code)

    def data(self, code, data):
        return make_response(jsonify(data), code)

    def error(self, exc): #error(self, exc_str, msg=""):
        # if isinstance(exc_str, object):
        #     exc_str = type(exc_str).__name__

        # exc = self.EXC_MAPPING.get(exc_str, InternalServerError)
        # if msg:
        #     exc = exc(msg)
        return make_response(str(exc), exc.code)

    def map_exceptions(self, exc, user_id):
        return self.EXC_MAPPING.get(exc["key"], InternalServerError)(exc["msg"], exc["service"], user_id)
