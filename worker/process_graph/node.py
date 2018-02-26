''' Process Node of the Process Graph'''

from os import environ
from abc import ABC, abstractmethod
from random import choice
from string import ascii_lowercase, digits
from requests import get
from json import loads
from worker.templates.persistant_volume_claim import PersistentVolumeClaim
from worker.templates.image_stream import ImageStream
from worker.templates.build_config import BuildConfig
from worker.templates.config_map import ConfigMap
from worker.templates.job import Job

class Node(ABC):
    ''' Base class for process nodes. '''

    def __init__(self, graph_id):
        rnd = "".join(choice(ascii_lowercase + digits) for _ in range(3))
        self.node_id = "{0}-n{1}-".format(graph_id, rnd)

    @abstractmethod
    def get_process_id(self):
        ''' Returns the process_id '''
        raise Exception("Not yet implemented!")

    @abstractmethod
    def get_arguments(self):
        ''' Returns the arguments '''
        raise Exception("Not yet implemented!")

    @abstractmethod
    def calculate_storage_size(self):
        ''' Calculates the needed storage of the node '''
        raise Exception("Not yet implemented!")

    @abstractmethod
    def get_sub_nodes(self):
        ''' Returns the child nodes '''
        raise Exception("Not yet implemented!")

    @staticmethod
    def get_node_spec(process_id):
        ''' Returns the process description of a specific backend '''

        url = "{0}/processes/{1}/details".format(environ.get("OPENEO_API"), process_id)
        response = get(url)
        response.raise_for_status()

        return loads(response.text)

    @staticmethod
    def parse_node(graph_id, p_payload):
        ''' Parses the process graph nodes '''

        from worker.process_graph.filter import Filter
        from worker.process_graph.operation import Operation

        if "product_id" in p_payload:
            return Filter(graph_id, p_payload)

        p_id = p_payload["process_id"]
        p_spec = Node.get_node_spec(p_id)

        if p_spec["process_type"] == "filter":
            return Filter(graph_id, p_payload)

        return Operation(graph_id, p_payload, p_spec)

    def run(self, token, namespace, storage_class):
        ''' Retrieves the file paths and executes filter process '''

        # Execute sub nodes
        input_pvcs = []
        sub_nodes = self.get_sub_nodes()
        for sub_node in sub_nodes:
            input_pvc = sub_node.run(token, namespace, storage_class)
            input_pvcs.append(input_pvc)

        # Get process specification
        process_id = self.get_process_id()
        node_spec = Node.get_node_spec(process_id)
        git_uri = node_spec["git_uri"]
        git_ref= node_spec["git_ref"]

        # Get arguments
        args = self.get_arguments()

        # Create output volume
        # TODO: Calculate volume size by file sizes (apdapt metadata db)
        # storage_size = self.calculate_storage_size()
        storage_size = "5Gi"
        out_pvc = PersistentVolumeClaim(namespace, self.node_id, storage_class, storage_size)
        #out_pvc.create(token)
        
        # Create Image Stream
        img_stream = ImageStream(namespace, self.node_id)
        #img_stream.create(token)

        # Create Build
        build_cfg = BuildConfig(namespace, self.node_id, git_uri, git_ref, img_stream)
        #build_cfg.create(token)

        # Create Config_Data
        conf_map = ConfigMap(namespace, self.node_id, args, input_pvcs)
        #conf_map.create(token)

        # Create Job
        job = Job(namespace, self.node_id, img_stream, input_pvcs, out_pvc, conf_map)
        #job.create(token)

        return out_pvc
