''' Process Graph '''

from os import environ
from request import post
from random import choice
from string import ascii_lowercase, digits
from .nodes.node import Node
from .nodes.utils import generate_random_id

class ProcessGraph:
    ''' The process graph class contains the executable graph nodes '''

    def __init__(self, job_id, payload):
        self.job_id = job_id
        payload["output"]["folder"] = job_id
        process_graph = {
            "process_id": "convert",
            "args": {
                "imagery": {
                    "process_id": payload["process_graph"]["process_id"],
                    "args": payload["process_graph"]["args"]
                },
                "output": payload["output"]
            }
        }

        self.start_node = Node.parse_node(job_id, process_graph)
        self.set_status("Initalized")

    def execute(self, token, namespace, storage_class):
        ''' Executes the process graph '''
        
        self.set_status("Running")
        
        end_pvc = self.start_node.run(token, namespace, storage_class)
        end_pvc.delete(token)
        
        self.set_status("Finished")

    def set_status(self, status):
        ''' Changes the status of job processing '''
        self.status = status
        
        response = post("{0}/jobs/{1}/status".format(environ.get("OPENEO_API"), self.job_id), data={"status":status})
        response.raise_for_status()
