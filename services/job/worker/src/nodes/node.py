''' Process Node of the Process Graph'''

from abc import ABC, abstractmethod
from .templates.persistant_volume_claim import PersistentVolumeClaim
from .templates.image_stream import ImageStream
from .templates.build_config import BuildConfig
from .templates.config_map import ConfigMap
from .templates.job import Job
from .requests.openeo import get_single
from .utils import generate_random_id

class Node(ABC):
    ''' Base class for process nodes. '''

    def __init__(self, graph_id):
        self.node_id = "{0}-n{1}".format(graph_id, generate_random_id(3))

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
    def parse_node(graph_id, p_payload):
        ''' Parses the process graph nodes '''

        from .filter import Filter
        from .operation import Operation

        if "product_id" in p_payload:
            return Filter(graph_id, p_payload)

        p_spec = get_single("openeo", "processes", p_payload["process_id"], "details")

        if p_spec["process_type"] == "filter":
            return Filter(graph_id, p_payload)

        return Operation(graph_id, p_payload, p_spec)

    def run(self, token, namespace, storage_class):
        ''' Retrieves the file paths and executes filter process '''

        # TODO Make data downloadable
        # TODO Pod Error identification and handling

        # Execute sub nodes and clean up
        input_pvcs = []
        sub_nodes = self.get_sub_nodes()
        for sub_node in sub_nodes:
            input_pvc = sub_node.run(token, namespace, storage_class)
            input_pvcs.append(input_pvc)

        # Get process specification
        process_id = self.get_process_id()
        node_spec = get_single("openeo", "processes", process_id, "details")

        git_uri = node_spec["git_uri"]
        git_ref= node_spec["git_ref"]
        git_dir = node_spec["git_dir"]

        # Get arguments
        args = self.get_arguments()

        # Create output volume
        # TODO: Calculate volume size by file sizes (apdapt metadata db)
        # storage_size = self.calculate_storage_size()
        storage_size = "5Gi"
        out_pvc = PersistentVolumeClaim(namespace, self.node_id, storage_class, storage_size)
        out_pvc.create(token)

        # Check if image does exist otherwise create
        img_stream = ImageStream(namespace, process_id)
        if not img_stream.does_exist(token):
            img_stream.create(token)
            build_cfg = BuildConfig(namespace, process_id, git_uri, git_ref, git_dir, img_stream)
            build_cfg.create(token)

        # Create Config_Data
        conf_map = ConfigMap(namespace, self.node_id, args, input_pvcs)
        conf_map.create(token)

        # Create Job
        job = Job(namespace, self.node_id, img_stream, input_pvcs, out_pvc, conf_map)
        job.create(token)

        # Clean Up
        conf_map.delete(token)
        job.delete(token)
        for input_pvc in input_pvcs:
            input_pvc.delete(token)

        return out_pvc

    