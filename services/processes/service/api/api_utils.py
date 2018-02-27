''' API Utilities '''

from functools import wraps
from json import loads
from requests import get
from flask import request, jsonify, current_app
from service.api.api_exceptions import AuthenticationError

def parse_response(code, msg=None, data=None):
    ''' Helper for Parsing JSON Response '''

    if msg and data:
        return jsonify({"message": str(msg), "data": data}), code

    if not msg:
        return jsonify(data), code
    
    if not data:
        return str(msg), code

def authenticate(f):
    ''' Create wrapper function for authtification '''

    @wraps(f)
    def decorated_function(*args, **kwargs):
        ''' Decorator function for authtification '''

        try:
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                raise AuthenticationError
            
            # TODO: Message Broker... 
            headers = {"Authorization": auth_header}
            response = get("http://" + current_app.config["OPENEO_API"] + "/auth/identify", headers=headers)

            if response.status_code != 200:
                raise AuthenticationError(response.text)

            user = loads(response.text)

            return f(user, *args, **kwargs)

        except AuthenticationError as exp:
            return parse_response(exp.code, str(exp))

    return decorated_function
