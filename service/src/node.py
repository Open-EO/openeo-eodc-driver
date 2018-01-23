''' Process Graph Parser '''

from json import loads, dumps
from requests import get, post
from flask import current_app
from service.src.tmp_processes import filterbbox, filterdaterange, ndvi, mintime, extractfromstorage
from service.src.filter import Filter, parse_urls

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
        if process_template["type"] == "filter":
            # TODO: Auch noch process template?
            # TODO: Add correct url from environ
            filter_graph = Filter(process_id, process_args)
            filter_urls = parse_urls("http://127.0.0.1:9002/data?p=0", filter_graph)

            self.process_id = "extract-from-storage"
            self.process_template = get_process_from_registry(self.process_id)
            self.process_args = {"urls": filter_urls}
        else:
            self.process_id = process_id
            self.process_template = process_template
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

                parsed_collections.append(
                    Node(
                        process_id,
                        process_args,
                        process_template
                    )
                )

            process_args["collections"] = parsed_collections

        return process_args

    def execute(self):
        return "Not yet implemented"

    def build(self):
        data = {
            "build_id": self.process_id,
            "build_namespace": "sandbox",
            "git_uri": self.process_template["git_uri"],
            "git_ref": self.process_template["git_ref"],
        }

        response = post("{0}/build".format(current_app.config["BUILD_CONTROLLER"]), json=data)

        if response.status_code != 201:
            raise ParsingException("Process {0} could not be build.".format(self.process_id))


    def deploy(self):
        data = {
            "build_id": self.process_id,
            "deploy_id": self.process_id,
            "namespace": "sandbox",
            "args": self.process_args
        }

        response = post("{0}/deploy".format(current_app.config["DEPLOY_CONTROLLER"]), json=data)
        print(response.text)
        if response.status_code != 201:
            raise ParsingException("Process {0} could not be deployed.".format(self.process_id))
