''' Data API of EODC Data Service '''

from flask import Blueprint, request
from flask_cors import cross_origin
from service.api.api_utils import parse_response, authenticate
# from service.src.csw import get_records, get_file_paths

DATA_BLUEPRINT = Blueprint("data", __name__)

@DATA_BLUEPRINT.route("/data", methods=["GET"])
@cross_origin(origins="*", supports_credentials=True)
@authenticate
def get_data(user):
    ''' Get data records from PyCSW server '''

    # TODO: CSW Implementation
    # Dummy data
    data = [
        {
            "product_id": "Sentinel-2A",
            "description": "Sentinel 2A: Multi-spectral data with 13 bands in the visible, near infrared, and short wave infrared part of the spectrum.",
            "source": "European Space Agency (ESA)"
        },
        {
            "product_id": "SENTINEL2-1C",
            "description": "Sentinel 2 Level-1C: Top-of-atmosphere reflectances in cartographic geometry",
            "source": "European Space Agency (ESA)"
        }
    ]

    return parse_response(200, data=data)

    # try:
    #     products = get_records(request.args.get('qname'),
    #                            request.args.get('qgeom'),
    #                            request.args.get('qstartdate'),
    #                            request.args.get('qenddate'))

    #     return parse_response(200, products)
    # except ConnectionError:
    #     return parse_response(503, {"message": "The service is currently unavailable."})

@DATA_BLUEPRINT.route("/data/paths", methods=["GET"])
@cross_origin(origins="*", supports_credentials=True)
@authenticate
def get_file_paths(user):
    ''' Get file paths to EODC storage files. '''

    # TODO: CSW Implementation
    # Dummy data
    data = [
        "/eodc/products/copernicus.eu/s2a_prd_msil1c/2017/01/01/S2A_MSIL1C_20170101T100412_N0204_R122_T31NFF_20170101T101120.zip",
        "/eodc/products/copernicus.eu/s2a_prd_msil1c/2017/01/01/S2A_MSIL1C_20170101T100412_N0204_R122_T31NEE_20170101T101120.zip",
        "/eodc/products/copernicus.eu/s2a_prd_msil1c/2017/01/01/S2A_MSIL1C_20170101T100412_N0204_R122_T31NFE_20170101T101120.zip",
        "/eodc/products/copernicus.eu/s2a_prd_msil1c/2017/01/01/S2A_MSIL1C_20170101T100412_N0204_R122_T31NDF_20170101T101120.zip",
        "/eodc/products/copernicus.eu/s2a_prd_msil1c/2017/01/01/S2A_MSIL1C_20170101T100412_N0204_R122_T31NCF_20170101T101120.zip",
        "/eodc/products/copernicus.eu/s2a_prd_msil1c/2017/01/01/S2A_MSIL1C_20170101T100412_N0204_R122_T31NEF_20170101T101120.zip"
    ]
    
    return parse_response(200, data=data)
    
    # try:
    #     products = get_file_paths(request.args.get('product_id'),
    #                               request.args.get('srs'),
    #                               request.args.get('left'),
    #                               request.args.get('right'),
    #                               request.args.get('top'),
    #                               request.args.get('end'),
    #                               request.args.get('from'),
    #                               request.args.get('to'))

    #     return parse_response(200, products)
    # except ConnectionError:
    #     return parse_response(503, {"message": "The service is currently unavailable."})
