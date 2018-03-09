''' /data route of Data Service '''

from os import environ
from flask import Blueprint, request
from .api_utils import parse_response, cors
from service.src.csw import get_records, CWSError

DATA_BLUEPRINT = Blueprint("data", __name__)

@DATA_BLUEPRINT.route("/data", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def options_data():
    return parse_response(200)

@DATA_BLUEPRINT.route("/data", methods=["GET"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def get_all_products():
    ''' Get data records from PyCSW server '''

    params = request.args
    product = params["qname"] if "qname" in params else None
    bbox = params["qgeom"] if "qgeom" in params else None
    begin = params["qstartdate"] if "qstartdate" in params else None
    end = params["qqenddatename"] if "qenddate" in params else None

    try:
        record = get_records(series=True, product="s2a_prd_msil1c")

        all_records = []
        all_records.append({
            "product_id": record[0]["dc:identifier"],
            "description": record[0]["dct:abstract"],
            "source": record[0]["dc:creator"],
        })

        # records = get_records(series=True, product=product, begin=begin, end=end, bbox=bbox)

        #TODO: Support all formats!
        # all_records = []
        # for record in records:
        #     all_records.append({
        #         "product_id": record["dc:identifier"],
        #         "description": record["dct:abstract"],
        #         "source": record["dc:creator"],
        #     })
        
        return parse_response(200, data=all_records)
    except CWSError as exp:
        print(str(exp))
        return parse_response(400, str(exp))

@DATA_BLUEPRINT.route("/data/<product_id>", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def options_data_item(product_id):
    return parse_response(200)

@DATA_BLUEPRINT.route("/data/<product_id>", methods=["GET"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def get_product(product_id):
    ''' Get data records from PyCSW server '''

    try:
        record = get_records(series=True, product=product_id)

        if not record:
            return parse_response(200, data={})

        return parse_response(200, data=record[0]) 
    except CWSError as exp:
        print(str(exp))
        return parse_response(400, str(exp))

@DATA_BLUEPRINT.route("/data/opensearch", methods=["OPTIONS"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def options_data_opensearch():
    return parse_response(200)

@DATA_BLUEPRINT.route("/data/opensearch", methods=["GET"])
@cors(auth=True, methods=["OPTIONS", "GET"])
def get_product_opensearch():
    ''' Get data records from PyCSW server '''
    return parse_response(501, "This API feature is not supported by the back-end.")
