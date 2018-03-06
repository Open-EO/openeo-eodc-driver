''' Get records from CSW server '''

from os import environ, path
from requests import post
from json import loads, dumps
from datetime import datetime, timedelta
from xml.dom.minidom import parseString

class CWSError(Exception):
    ''' CWSError raises if a error occures while querying the CSW server. '''
    def __init__(self, msg):
        super(CWSError, self).__init__(msg)

with open("worker/src/nodes/requests/get_records.xml") as xml_file:
        xml_file = xml_file.read()

def get_all_records(product, begin, end, bbox, just_filepaths=True):
    ''' Return the collected csw records of the query '''

    all_records = []
    record_next = 1

    while int(record_next) > 0:
        record_next, records = get_single_records(record_next, product, begin, end, bbox, just_filepaths)
        all_records += records
    
    return all_records

def get_single_records(start_position, product, begin, end, bbox, just_filepaths):
    ''' Return the records of a single request (max 100 records) '''

    xml_request = xml_file.format(start_position=start_position, product=product, begin=begin, end=end, bbox=bbox)
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
        print("{0}".format(dumps(response_json, indent=4, sort_keys=True) ))
        quit()

    search_result = response_json["csw:GetRecordsResponse"]["csw:SearchResults"]

    record_next = search_result["@nextRecord"]

    if not "csw:Record" in search_result:
        return 0, []

    records = search_result["csw:Record"]

    results = []
    if isinstance(records, list):
        for item in records:
            date = datetime.strptime(item["dc:date"], '%Y-%m-%dT%H:%M:%SZ')
            results.append([date, item["dct:references"]["#text"]] if just_filepaths else item)

    if isinstance(records, dict):
        date = datetime.strptime(records["dc:date"], '%Y-%m-%dTH:M:SZ')
        results.append([date, records["dct:references"]["#text"]] if just_filepaths else records)

    return record_next, results

def get_file_paths(product, t_from, t_to, bbox):
    ''' Get file paths from records '''

    start_date = datetime.strptime(t_from, '%Y-%m-%d')
    start_date = start_date - timedelta(days=1)
    start_date = start_date.strftime("%Y-%m-%dT00:00:00Z")
    
    end_date = datetime.strptime(t_to, '%Y-%m-%d')
    end_date = end_date + timedelta(days=1)
    end_date = end_date.strftime("%Y-%m-%dT23:59:59Z")

    records = get_all_records(product, start_date, end_date, bbox)

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
