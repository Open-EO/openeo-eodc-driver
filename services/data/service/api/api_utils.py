''' API Utilities '''

from functools import wraps
from json import loads
from requests import get
from flask import request, jsonify, current_app, make_response
from .api_exceptions import AuthenticationError

def parse_response(code, msg=None, data=None):
    ''' Helper for Parsing JSON Response '''

    if not msg and not data:
        return "", code

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
            
            # TODO: Message Broker
            headers = {"Authorization": auth_header}
            response = get(current_app.config["OPENEO_API"] + "/auth/identify", headers=headers)

            if response.status_code != 200:
                raise AuthenticationError(response.text)

            user = loads(response.text)

            return f(user, *args, **kwargs)

        except AuthenticationError as exp:
            return parse_response(exp.code, str(exp))

    return decorated_function

def cors(origins=["*"], auth=False, methods=["GET"]):
    """This decorator adds the headers passed in to the response"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            if "Origin" in request.headers:
                allow_origins = request.headers.get('Origin')
            else:
                 allow_origins = "*"

            allow_methods = ""
            for method in methods: 
                allow_methods += method + ","
            allow_methods = allow_methods[:-1]

            response = make_response(f(*args, **kwargs))

            response.headers.add('Access-Control-Allow-Origin', allow_origins)
            response.headers.add('Access-Control-Allow-Methods', allow_methods)

            allow_headers = "Content-Type"

            if auth:
                allow_headers += ", Authorization"
                response.headers.add('Access-Control-Allow-Credentials', "true")
            
            response.headers.add('Access-Control-Allow-Headers', allow_headers)

            return response
        return decorated_function
    return decorator
