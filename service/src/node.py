''' Process Graph Parser '''

from json import loads
from requests import get
from flask import current_app
from tmp_data import filterbbox, filterdaterange, ndvi, mintime, extractfromstorage
from filter import Filter, parse_urls

class ParsingException(Exception):
    ''' Parsing Exception raises if process_graph is not processable '''
    pass

def parse_process_graph(process_graph):
    ''' Parsing the process graph and returning the start node '''

    process_id = process_graph["process_id"]
    process_args = process_graph["args"]
    process_template = get_process_from_registry(process_id)

    return Node(process_id, process_args, process_template)

def get_process_from_registry(process_id):
    ''' Query the registry to get the process_id. '''

    # TODO: Send user token for namespace validation 
    # response = get("{0}/processes/{1}".format(current_app.config["PROCESS_REGISTRY"],
    #                                           self.process_id))
    # if response.status_code != 200:
    #     raise ParsingException("Process {0} could not be found in your process \
    #                             registry namespaces.".format(self.process_id))
    # TODO: Prozess in welchem namespace? -> 0
    # process = loads(response.text)["data"]["process"][0]

    if process_id == "filter_bbox":
        return filterbbox

    if process_id == "filter_daterange":
        return filterdaterange

    if process_id == "extract-from-storage":
        return extractfromstorage

    if process_id == "NDVI":
        return ndvi

    if process_id == "min_time":
        return mintime

class Node:
    ''' Executable node objects of the process graph '''

    def __init__(self, process_id, process_args, process_template):
        self.process_id = process_id
        self.process_args = self.parse_args(process_args, process_template["args"])

    def parse_args(self, process_args, validate_args):
        ''' Validates the arguments triggers recursive Node parsing. '''

        # Validate if all required arguments are available
        for arg in validate_args.keys():
            if validate_args[arg]["required"]:
                if arg not in process_args:
                    raise ParsingException("Missing argument {0} for process {1}." \
                                            .format(arg, self.process_id))

        parsed_collections = []
        if "collections" in process_args:
            for collection in process_args["collections"]:
                process_id = collection["process_id"]
                process_args = collection["args"]
                process_template = get_process_from_registry(collection["process_id"])

                if process_template["type"] == "filter":
                    # TODO: Auch noch process template?
                    filter_graph = Filter(process_id, process_args)
                    # TODO: Add correct url from environ
                    filter_urls = parse_urls("http://www.test.de", filter_graph)

                    process_id = "extract-from-storage"
                    parsed_collections.append(Node(
                        process_id,
                        {"urls": filter_urls},
                        get_process_from_registry(process_id)
                    ))
                else:
                    parsed_collections.append(Node(
                        process_id,
                        process_args,
                        process_template
                    ))

            process_args["collections"] = parsed_collections

        return process_args

        def execute(self):
            return "Not yet implemented"

        def build(self):
            return "Not yet implemented"

        def deploy(self):
            return "Not yet implemented"
