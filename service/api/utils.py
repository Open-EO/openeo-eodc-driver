''' Utils for benchmarking service '''

from flask import jsonify


STATUS_CODE = {
    200: "OK",
    201: "CREATED",
    400: "Bad Request"
}


def parse_response(code, msg, data=None):
    ''' Helper for parsing response json '''

    res_obj = {
        "status": STATUS_CODE[code],
        "message": msg
    }

    if data:
        res_obj["data"] = data

    return jsonify(res_obj), code
