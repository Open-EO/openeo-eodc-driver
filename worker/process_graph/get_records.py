''' Get records from CSW server '''

from os import environ, path
from requests import post
from json import loads, dumps
from xml.dom.minidom import parseString

with open("worker/templates/get_records.xml") as xml_file:
        xml_file = xml_file.read()

class CWSError(Exception):
    ''' CWSError raises if a error occures while querying the CSW server. '''
    def __init__(self, msg):
        super(CWSError, self).__init__(msg)

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
    for item in records:
        if just_filepaths: 
            results.append(item["dct:references"]["#text"])
        else:
            results.append(item)

    return record_next, results

# if __name__ == "__main__":
#     product = "s2a_prd_msil1c"
#     begin = "2018-01-01T12:00:00Z"
#     end = "2018-01-15T12:00:00Z"
#     bbox = [47, -5, 55, 20]

#     records = get_all_records(product, begin, end, bbox)