''' Communication with pyCSW metadata backend '''

import re
from owslib.fes import PropertyIsLike, BBox, PropertyIsLessThanOrEqualTo, PropertyIsGreaterThanOrEqualTo, SortBy, SortProperty
# from service import CSW_SERVER
from shapely.geometry.base import geom_from_wkt, WKTReadingError
from pprint import pprint

def get_file_paths(req_product_id, req_srs, req_left, req_right, req_top, req_end, req_from, req_to):
    ''' Get the EODC Storage file paths of the queried data '''
    # constraints = []
    # constraints.append(BBox([req_end, req_left, req_top, req_right]))
    # constraints.append(PropertyIsLike('dc:subject', "%" + req_product_id + "%"))
    # constraints.append(PropertyIsGreaterThanOrEqualTo('apiso:TempExtent_begin', req_from + "T00:00:00"))
    # constraints.append(PropertyIsLessThanOrEqualTo('apiso:TempExtent_end', req_to + "T23:59:59"))
    # data_sortby = SortBy([SortProperty("apiso:TempExtent_begin", "ASC")])

    # all_products = []
    # startposition = 0

    # running = True
    # while running:
    #     print(startposition)
    #     CSW_SERVER.getrecords2(constraints=constraints,
    #                            maxrecords=100,
    #                            startposition=startposition,
    #                            esn='full',
    #                            sortby=data_sortby)

    #     for key, record in CSW_SERVER.records.items():
    #         print(key)
    #         product_id = re.split(r"_\d{8}T", key)[0].replace("_", "")

    #         exists = False
    #         for product in all_products:
    #             if product_id in product["product_id"]:
    #                 product["reference"].append(record.references[0]["url"])
    #                 exists = True

    #         if not exists:
    #             all_products.append({record.references[0]["url"]})

    #     startposition += 100
    #     if startposition > 0:
    #         for product in all_products:
    #             product["matches"] = len(product["data"])
    #         break

    data = [
        "/eodc/products/copernicus.eu/s2a_prd_msil1c/2017/01/01/S2A_MSIL1C_20170101T100412_N0204_R122_T31NFF_20170101T101120.zip",
        "/eodc/products/copernicus.eu/s2a_prd_msil1c/2017/01/01/S2A_MSIL1C_20170101T100412_N0204_R122_T31NEE_20170101T101120.zip",
        "/eodc/products/copernicus.eu/s2a_prd_msil1c/2017/01/01/S2A_MSIL1C_20170101T100412_N0204_R122_T31NFE_20170101T101120.zip",
        "/eodc/products/copernicus.eu/s2a_prd_msil1c/2017/01/01/S2A_MSIL1C_20170101T100412_N0204_R122_T31NDF_20170101T101120.zip",
        "/eodc/products/copernicus.eu/s2a_prd_msil1c/2017/01/01/S2A_MSIL1C_20170101T100412_N0204_R122_T31NCF_20170101T101120.zip",
        "/eodc/products/copernicus.eu/s2a_prd_msil1c/2017/01/01/S2A_MSIL1C_20170101T100412_N0204_R122_T31NEF_20170101T101120.zip"
    ]

    return data

def get_records(keywords=None, poly=None, tempextent_begin=None, tempextent_end=None, maxrecords=1000):
    ''' Get data record from pycsw backend '''

    constraints = []

    # if poly is not None:
    #     bbox = poly_to_bbox(poly)
    #     if bbox != [-90, -180, 90, 180] and bbox is not None:
    #         constraints.append(BBox(bbox))

    # if keywords is not None:
    #     keywords = keywords.split(",")

    #     for keyword in keywords:
    #         kw = keyword.strip()
    #         if kw == "":
    #             continue
    #         constraints.append(PropertyIsLike(
    #             'dc:subject', "%" + kw + "%"))

    # if tempextent_begin is not None:
    #     constraints.append(PropertyIsGreaterThanOrEqualTo(
    #         'apiso:TempExtent_begin', tempextent_begin))

    # if tempextent_end is not None:
    #     constraints.append(PropertyIsLessThanOrEqualTo(
    #         'apiso:TempExtent_end', tempextent_end))

    # if len(constraints) > 1:
    #     constraints = [constraints]

    # sortby = SortBy([SortProperty("apiso:TempExtent_begin", "ASC")])

    # all_products = []
    # startposition = 0

    # running = True
    # while running:
    #     CSW_SERVER.getrecords2(constraints=constraints,
    #                            maxrecords=maxrecords,
    #                            startposition=startposition,
    #                            esn='full',
    #                            sortby=sortby)

    #     for key, record in CSW_SERVER.records.items():
    #         product_id = re.split(r"_\d{8}T", key)[0].replace("_", "")

    #         exists = False
    #         for product in all_products:
    #             if product_id in product["product_id"]:
    #                 product["data"].append(record.identifier)
    #                 product["reference"].append(record.references[0]["url"])
    #                 exists = True

    #         if not exists:
    #             all_products.append({
    #                 "product_id": product_id,
    #                 "subjects": record.subjects,
    #                 "abstract": record.abstract,
    #                 "creator": record.creator,
    #                 "data": [record.identifier],
    #                 "reference": [record.references[0]["url"]]})

    #     startposition += maxrecords
    #     if startposition > 0:
    #         for product in all_products:
    #             product["matches"] = len(product["data"])
    #         break

    return True #all_products


def poly_to_bbox(wkt_string):
    """
    Gets the bounding box of the dataset from from wkt_geometry.
    """
    try:
        # check if polygon is closed:
        coordinates = wkt_string[9:-2]
        coord = coordinates.split(",")

        # if polygon is not closed, close it:
        if coord[0] != coord[-1]:
            coordinates += "," + coord[0]
            wkt = "POLYGON((" + coordinates + "))"

        poly = geom_from_wkt(wkt)
        return poly.bounds
    except WKTReadingError:
        raise WKTReadingError("LinearRing not closed")

def test_q(name):
    # CSW_SERVER.getrecords2(constraints=[PropertyIsLike('dc:subject', "%" + name.strip() + "%")],
    #                 maxrecords=1000,
    #                 startposition=0,
    #                 esn='full',
    #                 sortby=SortBy([SortProperty("apiso:TempExtent_begin", "ASC")]))
    return {}