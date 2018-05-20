from flask import make_response, jsonify
from .cors import response_headers


class OK:
    code = 200

    def __init__(self, msg):
        self.msg = msg

    def __parse__(self):
        return {
            "description": self.msg,
            "headers": response_headers
        }


class BadRequest(Exception):
    code = 400
    msg = "The server cannot or will not process the request due to an apparent client error."

    def __parse__(self):
        return {"description": self.msg}


class Unauthorized(Exception):
    code = 401
    msg = "The back-end requires clients to authenticate in order to process this request. Your account may not be activated."

    def __parse__(self):
        return {"description": self.msg}


class Forbidden(Exception):
    code = 403
    msg = "Authorization failed, access to the requested resource has been denied."

    def __parse__(self):
        return {"description": self.msg}


class NotFound(Exception):
    code = 404
    msg = "The requested resource could not be found but may be available in the future."

    def __parse__(self):
        return {"description": self.msg}


class MethodNotAllowed(Exception):
    code = 405
    msg = "The requested HTTP method is not supported or allowed to be requested."

    def __parse__(self):
        return {"description": self.msg}


class NotAcceptable(Exception):
    code = 406
    msg = "The server is not capable to deliver the requested format."

    def __parse__(self):
        return {"description": self.msg}


class Conflict(Exception):
    code = 409
    msg = "The request could not be processed because of conflict in the request. An entity with the same id might already exist."

    def __parse__(self):
        return {"description": self.msg}


class InternalServerError(Exception):
    code = 500
    msg = "The request can't be fulfilled due to an error at the back-end."

    def __parse__(self):
        return {"description": self.msg}


class NotImplemented(Exception):
    code = 501
    msg = "This API feature is not supported by the back-end."

    def __parse__(self):
        return {"description": self.msg}


class ServiceUnavailable(Exception):
    code = 503
    msg = "The service is currently unavailable."

    def __parse__(self):
        return {"description": self.msg}


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

    def error(self, exc, msg=""):
        exc = self.EXC_MAPPING.get(type(exc()).__name__, InternalServerError)
        if msg:
            exc = exc(msg)
        return make_response(exc.msg, exc.code)

    def map_exceptions(self, exc_string):
        return self.EXC_MAPPING.get(exc_string, "InternalServerError")
