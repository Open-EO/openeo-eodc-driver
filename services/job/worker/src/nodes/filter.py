''' Filter Node of Process Graph '''

from pyproj import Proj, transform
from .requests.csw import get_file_paths
from .node import Node

class Filter(Node):
    ''' Filter node for filtering products, time ranges and bands '''

    def __init__(self, graph_id, filter_payload):
        super().__init__(graph_id)

        if "product_id" in filter_payload:
            self.filter_id = "product"
            self.args = {"product_id": filter_payload["product_id"]}
            self.input_nodes = []
            return 

        self.filter_id = filter_payload["process_id"]

        self.args = {}
        self.input_nodes = []
        for key, value in filter_payload["args"].items():
            if key == "imagery":
                input_node = Node.parse_node(graph_id, value)
                self.input_nodes.append(input_node)
            else:
                self.args[key] = value

    def get_process_id(self):
        ''' Returns the process_id '''
        return "filter-s2"
    
    def get_filter_arguments(self, args):
        ''' Merges the arguments of the filter node chain'''

        for key, value in self.args.items():
            args[key] = value

        for input_node in self.input_nodes:
            input_node.get_filter_arguments(args)

    def get_arguments(self):
        ''' Returns the arguments of all sub nodes '''

        # Get the args of the sub filter nodes
        args = {"file_paths": {}}
        self.get_filter_arguments(args)

        # TODO: Band filtering, if empty -> All bands
        if not "bands" in args:
            args["bands"] = []

        # Get the file_paths from CSW server
        in_proj = Proj(init=args["srs"])
        out_proj = Proj(init='epsg:4326')
        in_x1, in_y1 = args["bottom"], args["left"]
        in_x2, in_y2 = args["top"], args["right"]
        out_x1, out_y1 = transform(in_proj, out_proj, in_x1, in_y1)
        out_x2, out_y2 = transform(in_proj, out_proj, in_x2, in_y2)

        bbox = [out_x1, out_y1, out_x2, out_y2]
        args["file_paths"] = get_file_paths(args["product_id"], args["from"], args["to"], bbox)
        
        return args

    def calculate_storage_size(self, token, namespace, storage_class):
        ''' Calculates the needed storage of the node '''

        # TODO: Calculate storage size by file_sizes
        return "5Gi"

    def get_sub_nodes(self):
        ''' Returns the child nodes '''

        # TODO: Implement for filter if Core API integrates Array of imaginary
        return []
