''' /data route of Data Service '''

from flask import Blueprint, redirect
from .api_utils import cors, parse_response

MAIN_BLUEPRINT = Blueprint("main", __name__)

@MAIN_BLUEPRINT.route("/", methods=["OPTIONS"])
@cors()
def options():
    return parse_response(200)

@MAIN_BLUEPRINT.route("/", methods=["GET"])
@cors()
def get_all_products():
    ''' Get data records from PyCSW server '''
    return redirect("/capabilities", code=302)
