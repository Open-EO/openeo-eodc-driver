''' Get records from CSW server '''

from os import environ, path
from requests import post
from json import loads, dumps
from re import match
from datetime import datetime, timedelta
from xml.dom.minidom import parseString
from shapely.geometry.base import geom_from_wkt, WKTReadingError
from .xml_templates import xml_base, xml_and, xml_series, xml_product, xml_begin, xml_end, xml_bbox

class CWSError(Exception):
    ''' CWSError raises if a error occures while querying the CSW server. '''
    def __init__(self, msg):
        super(CWSError, self).__init__(msg)

def get_records(product=False, begin=False, end=False, bbox=False, just_filepaths=False, series=False):
    ''' Return the collected csw records of the query '''

    xml_filters = []
    if series: 
        xml_filters.append(xml_series)

    if product:
        if series:
            xml_filters.append(xml_product.format(property="dc:identifier", product=product))
        else:
            xml_filters.append(xml_product.format(property="apiso:ParentIdentifier", product=product))

    if begin:
        try:
            datetime.strptime(begin, '%Y-%m-%d')
        except ValueError:
            raise CWSError("Wrong format of begin date.")

        begin += "T00:00:00Z"
        xml_filters.append(xml_begin.format(begin=begin))

    if end: 
        try:
            datetime.strptime(end, '%Y-%m-%d')
        except ValueError:
            raise CWSError("Wrong format of end date.")

        end += "T23:59:59Z"

        if not series:
            xml_filters.append(xml_end.format(end=end))

    if bbox: 
        if isinstance(bbox, str):
            try:
                bbox = poly_to_bbox(bbox)
            except WKTReadingError:
                raise CWSError("Wrong format of WKT polygon.")

        if isinstance(bbox, list) and len(bbox) == 4:
            xml_filters.append(xml_bbox.format(bbox=bbox))
        else:
            raise CWSError("Invalid format of BBox")
        
    if len(xml_filters) == 0:
        return []
    
    filter_parsed = ""
    if len(xml_filters) == 1:
        filter_parsed = xml_filters[0]
    else:
        tmp_filter = ""
        for xml_filter in xml_filters:
            tmp_filter += xml_filter
        filter_parsed = xml_and.format(children=tmp_filter)

    all_records = []
    record_next = 1
    while int(record_next) > 0:
        record_next, records = get_single_records(record_next, filter_parsed, just_filepaths)
        all_records += records
    
    return all_records

def get_single_records(start_position, filer_parsed, just_filepaths):
    ''' Return the records of a single request '''
    
    xml_request = xml_base.format(children=filer_parsed, start_position=start_position)
    response = post(environ.get("CSW_SERVER"), data=xml_request)

    if not response.ok:
        print("Server Error {0}: {1}".format(response.status_code, response.text))
        raise CWSError("Error while communicating with CSW server.")

    if response.text.startswith("<?xml"):
        xml = parseString(response.text)
        print("{0}".format(xml.toprettyxml()))
        raise CWSError("Error while communicating with CSW server.")

    response_json = loads(response.text)

    if "ows:ExceptionReport" in response_json:
        print("{0}".format(dumps(response_json, indent=4, sort_keys=True)))
        raise CWSError("Error while communicating with CSW server.")

    search_result = response_json["csw:GetRecordsResponse"]["csw:SearchResults"]

    record_next = search_result["@nextRecord"]

    if not "csw:Record" in search_result:
        return 0, []

    records = search_result["csw:Record"]

    if not isinstance(records, list):
        records = [records]

    results = []
    for item in records:

        if just_filepaths:
            date = datetime.strptime(item["dc:date"], '%Y-%m-%dTH:M:SZ')
            results.append([date, item["dct:references"]["#text"]])
            continue

        results.append(item)

    return record_next, results

def get_file_paths(product, t_from, t_to, bbox):
    ''' Get file paths from records '''

    start_date = datetime.strptime(t_from, '%Y-%m-%d')
    start_date = start_date - timedelta(days=1)
    start_date = start_date.strftime("%Y-%m-%dT00:00:00Z")
    
    end_date = datetime.strptime(t_to, '%Y-%m-%d')
    end_date = end_date + timedelta(days=1)
    end_date = end_date.strftime("%Y-%m-%dT23:59:59Z")

    records = get_records(product, start_date, end_date, bbox, just_filepaths=True)

    day_sorting = []
    for idx, record in enumerate(records):
        name = record[0].strftime("%Y-%m-%d")

        if idx == 0:
            day_sorting.append([name, record[1]])
            continue

        time_diff = record[0] - records[idx-1][0]
        day_sorting.append([name if time_diff.days > 0 else day_sorting[idx-1][0], record[1]])
        
    file_paths = {}
    for item in day_sorting:
        if item[0] in file_paths:
            file_paths[item[0]].append(item[1])
            continue
        
        file_paths[item[0]] = [item[1]]

    return file_paths

def poly_to_bbox(wkt_string):
    """
    Gets the bounding box of the dataset from from wkt_geometry.
    """
    # check if polygon is closed:
    coordinates = wkt_string[9:-2]
    coord = coordinates.split(",")

    # if polygon is not closed, close it:
    if coord[0] != coord[-1]:
        coordinates += "," + coord[0]
        wkt = "POLYGON((" + coordinates + "))"

    poly = geom_from_wkt(wkt)
    return list(poly.bounds)

if __name__ == "__main__":

    try:
        product = "s2a_prd_msil1c"
        begin = "2016-01-01"
        end = "2018-01-15"
        bbox = "((30 10, 40 40, 20 40, 10 20))"

        records = get_records(series=True, begin=begin)
        stop = 1
    except CWSError as exp:
        print(str(exp))
