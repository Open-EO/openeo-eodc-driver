access_control_allow_origin = {
    "type": "string",
    "description": "Allowed origin of the request. Should return the value of the request`s origin header.",
    "default": "*"
}

access_control_allow_methods = {
    "type": "array",
    "description": "Comma-separated list of HTTP methods allowed to be requested. List all implemented HTTP methods for the endpoint here.",
    "collectionFormat": "csv",
    "items": {
        "type": "string"
    }
}

access_control_allow_headers = {
    "type": "array",
    "description": "Comma-separated list of HTTP headers allowed to be send. If the back-end requires authorization it needs to contain at least `Authorization`",
    "collectionFormat": "csv",
    "items": {
        "type": "string"
    }
}

access_control_allow_credentials = {
    "type": "boolean",
    "description": "If authorization is required by the back-end it needs to be set to `true`",
}

content_type = {
    "type": "string",
    "description": "Should return the content type delivered by the request that the permission is requested for."
}

response_headers = {
    "Access-Control-Allow-Origin": access_control_allow_origin,
    "Access-Control-Allow-Credentials": access_control_allow_credentials,
    "Content-Type": content_type
}


class CORS:
    def __parse__(self, parameters=[]):
        return {
            "tags": ["CORS"],
            "summary": "Response to allow Cross-Origin Resource Sharing.",
            "description": (
                "Response for the preflight requests made by some clients due to "
                "Cross-Origin Resource Sharing restrictions. It sends the appropriate "
                "headers for this endpoint as defined in the section 'Responses'. "
                "See https://www.w3.org/TR/cors/ for more information."),
            "parameters": parameters,
            "responses": {
                "200": {
                    "description": "Gives internet browsers the permission to access the requested resource.",
                    "headers": {
                        "Access-Control-Allow-Origin": access_control_allow_origin,
                        "Access-Control-Allow-Methods": access_control_allow_methods,
                        "Access-Control-Allow-Headers": access_control_allow_headers,
                        "Access-Control-Allow-Credentials": access_control_allow_credentials,
                        "Content-Type": content_type
                    }
                },
                "405": {
                    "description": "The requested HTTP method is not supported or allowed to be requested."
                }
            }
        }
