''' /data route of Data Service '''

from os import environ
from flask import Blueprint, request
from flask_cors import cross_origin
from service.api.api_utils import parse_response, authenticate
from requests import get
from json import loads

DATA_BLUEPRINT = Blueprint("data", __name__)

MAPPING = [

]

@DATA_BLUEPRINT.route("/data", methods=["GET"])
@cross_origin(origins="*", supports_credentials=True)
def get_data():
    ''' Get data records from PyCSW server '''
    
    url = "{0}?service=CSW&version=2.0.2&request=GetRecords"
    url += "&typenames=csw:Record&elementSetName=full"
    url += "&resultType=results&constraintLanguage=CQL_TEXT"
    url += "&startposition=1&outputFormat=application/json"
    url += "&constraint=apiso:Type = 'series'"
    url = url.format(environ.get("CSW_SERVER"))
    
    response = get(url)

    if response.ok == False:
        parse_response(503, "The service is currently unavailable.")
    
    response_json = loads(response.text)
    search_result = response_json["csw:GetRecordsResponse"]["csw:SearchResults"]
    records = search_result["csw:Record"]

    all_records = []
    for item in records:
        all_records.append(
            {
                "product_id": item["dc:identifier"],
                "description": item["dct:abstract"],
                "source": item["dc:creator"],
                "subjects": item["dc:subject"],
                "extent": item["ows:BoundingBox"],
            }
        )

    return parse_response(200, data=all_records)
