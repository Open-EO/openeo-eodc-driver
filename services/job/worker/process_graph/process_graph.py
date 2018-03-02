''' Process Graph '''

from os import environ
from random import choice
from string import ascii_lowercase, digits
from requests import post
from worker.process_graph.node import Node
from worker.exceptions import ProcessingError

class ProcessGraph:
    ''' The process graph class contains the executable graph nodes '''

    def __init__(self, job_id, payload):
        
        self.job_id = job_id
        rnd = "".join(choice(ascii_lowercase + digits) for _ in range(3))
        self.graph_id = "j{0}-g{1}".format(job_id, rnd)
        self.start_node = Node.parse_node(self.graph_id, payload["process_graph"])
        self.set_status("Initalized")

    def execute(self, token, namespace, storage_class):
        ''' Executes the process graph '''
        
        try:
            result_pvc = self.start_node.run(token, namespace, storage_class)
        except ProcessingError as exp:
            self.set_status("Processing Error:" + str(exp))
    
    def set_status(self, status):
        ''' Chnages the status of job processing '''
        self.status = status

        # response = post("{0}/jobs/{1}/status".format(environ.get("OPENEO_API"), self.job_id))

        # if not response.ok:
        #     print("Server Error {0}: {1}".format(response.status_code, response.text))
        #     raise Exception("Error while communicating with OpenShift API.")



