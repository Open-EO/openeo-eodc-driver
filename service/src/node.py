''' Process Graph Parser '''

from json import loads, dumps
from requests import get, post
from flask import current_app
from service.src.filter import Filter

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
    response = get("{0}/processes/{1}".format(current_app.config["PROCESS_REGISTRY"], process_id))
    if response.status_code != 200:
        raise ParsingException("Process {0} could not be found in your process \
                                registry namespaces.".format(process_id))

    # TODO: Prozess in welchem namespace? -> 0
    return loads(response.text)["data"]["process"][0]

class Node:
    ''' Executable node objects of the process graph '''

    def __init__(self, process_id, process_args, process_template):
        # if process_template["type"] == "filter":
        if True:
            # TODO: Auch noch process template?
            # TODO: Add correct url from environ
            filter_graph = Filter(process_id, process_args)

            self.process_id = "extract-from-storage"
            self.process_template = get_process_from_registry(self.process_id)
            self.process_args = {"file_paths": filter_graph.get_paths()}
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
            "image_stream": {
                "name": self.process_id + "-image",
                "namespace": "sandbox",
                "tag": "latest"
            },
            "build_config": {
                "name": self.process_id + "-build",
                "namespace": "sandbox",
                "git_uri": self.process_template["git_uri"],
                "git_ref": self.process_template["git_ref"],
                "image_name": self.process_id + "-image",
                "tag": "latest"
            }
        }

        response = post("{0}/build".format(current_app.config["TEMPLATE_ENGINE"]), json=data)

        if response.status_code != 201:
            print(response.text)
            raise ParsingException("Process {0} could not be build.".format(self.process_id))


    def deploy(self):
        data = {
            "pvc": {
                "name": self.process_id + "-pvc",
                "namespace": "sandbox",
                "class_name": "storage-write",
                "modes": "ReadWriteOnce",
                "size": "5Gi"
            },
            "config_map": {
                "name": self.process_id + "-configmap",
                "namespace": "sandbox",
                "data": { "file_paths": self.process_args["file_paths"]}
            },
            "job": {
                "name": self.process_id + "-job",
                "namespace": "sandbox",
                "image_name": self.process_id + "-image",
                "tag": "latest",
                "name_pvc": self.process_id + "-pvc",
                "name_configmap": self.process_id + "-configmap"
            }
        }

        response = post("{0}/deploy".format(current_app.config["TEMPLATE_ENGINE"]), json=data)

        if response.status_code != 201:
            raise ParsingException("Process {0} could not be deployed.".format(self.process_id))
