''' Utilities for EODC Job Service '''

from functools import wraps
from json import loads
from requests import get
from flask import request, jsonify, current_app

def parse_response(code, msg=None, data=None):
    ''' Helper for Parsing JSON Response '''

    if msg and data:
        jsonify({"message": msg, "data": data}), code

    if not msg:
        return jsonify(data), code
    
    if not data:
        return msg, code

def authenticate(f):
    ''' Create wrapper function for authtification '''

    @wraps(f)
    def decorated_function(*args, **kwargs):
        ''' Decorator function for authtification '''

        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return parse_response(403, "Authorization failed, access to the requested resource has been denied.")

        headers = {"Authorization": auth_header}
        response = get(current_app.config["OPENEO_API"] + "/auth/status", headers=headers)

        if response.status_code != 200:
            return parse_response(401, "The back-end requires clients to authenticate in order to process this request.")

        user = loads(response.text)["data"]

        return f(user, *args, **kwargs)

    return decorated_function