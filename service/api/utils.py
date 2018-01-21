''' Utilities for EODC Job Service '''

from flask import jsonify


STATUS_CODE = {
    200: "OK",
    201: "CREATED",
    400: "BAD REQUEST",
    404: "NOT FOUND"
}


def parse_response(code, msg, data=None):
    ''' Helper for Parsing JSON Response '''

    res_obj = {
        "status": STATUS_CODE[code],
        "message": msg
    }

    if data:
        res_obj["data"] = data

    return jsonify(res_obj), code
