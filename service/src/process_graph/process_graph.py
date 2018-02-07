''' The process graph class contains the executable graph nodes '''

from requests import get
from flask import current_app
from service.src.process_graph.node import Node

class ProcessGraph:
    def __init__(self, payload):
        self.end_node = ProcessGraph.parse_node(payload["process_graph"])

    @staticmethod
    def parse_node(node_payload):
        ''' Parses the process graph nodes '''

        process_specs = ProcessGraph.get_process_specs(node_payload["process_id"])

        if process_specs["type"] == "filter":
            extract_node = {
                "process_id": "extract_from_storage",
                "args": {
                    "filter_graph": node_payload
                }
            }

            return Node(extract_node)

        return Node(node_payload)

    @staticmethod
    def get_process_specs(process_id):
        response = get("/processes/" + process_id)

        stop = 1
        return {}

