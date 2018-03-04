''' Process Graph '''

from os import environ
from random import choice
from string import ascii_lowercase, digits
from requests import post
from worker.process_graph.node import Node
from worker.exceptions import ProcessingError
from worker.process_graph.utils import generate_random_id

class ProcessGraph:
    ''' The process graph class contains the executable graph nodes '''

    def __init__(self, job_id, payload):
        self.graph_id = "j{0}-g{1}".format(job_id, generate_random_id())

        payload["output"]["folder"] = self.graph_id

        process_graph = {
            "process_graph": {
                "process_id":"convert",
                "args": {
                    "imagery": {
                        "process_id": payload["process_graph"]
                    },
                    "output": payload["output"]
                }
            }
        }

        self.start_node = Node.parse_node(self.graph_id, process_graph)
        self.set_status("Initalized")

    def execute(self, token, namespace, storage_class):
        ''' Executes the process graph '''
        self.start_node.run(token, namespace, storage_class)

    def set_status(self, status):
        ''' Chnages the status of job processing '''
        self.status = status

        # response = post("{0}/jobs/{1}/status".format(environ.get("OPENEO_API"), self.job_id))

        # if not response.ok:
        #     print("Server Error {0}: {1}".format(response.status_code, response.text))
        #     raise Exception("Error while communicating with OpenShift API.")



