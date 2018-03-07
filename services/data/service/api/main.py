''' /data route of Data Service '''

from flask import Blueprint, redirect
from flask_cors import cross_origin

MAIN_BLUEPRINT = Blueprint("main", __name__)

@MAIN_BLUEPRINT.route("/", methods=["GET"])
@cross_origin(origins="*", supports_credentials=False, methods="GET")
def get_all_products():
    ''' Get data records from PyCSW server '''
    return redirect("/capabilities", code=302)
