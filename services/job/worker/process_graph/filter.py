''' Filter Node of Process Graph '''

from os import environ
from datetime import datetime, timedelta
from requests import get
from json import loads
from worker.process_graph.node import Node
from worker.process_graph.get_records import get_all_records
from random import choice
from string import ascii_lowercase, digits

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
       
    def daterange(self, start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def get_arguments(self):
        ''' Returns the arguments of all sub nodes '''

        # Get the args of the sub filter nodes
        args = {"file_paths": {}}
        self.get_filter_arguments(args)

        # Get the file_paths from CSW server

        # product = args["product_id"] #TODO Mapping of products
        product = "s2a_prd_msil1c"
        bbox = [args["bottom"], args["left"], args["top"], args["right"]]
        start_date = datetime.strptime(args["from"], '%Y-%m-%d')
        end_date = datetime.strptime(args["to"], '%Y-%m-%d')
        
        # TODO: Band filtering
        args["bands"] = ["B01"]

        if int ((end_date - start_date).days) == 0:
            day = start_date
            day_start = day.strftime("%Y-%m-%dT00:00:00Z")
            day_end = day.strftime("%Y-%m-%dT23:59:59Z")
            args["file_paths"][day.strftime("%Y-%m-%d")] = get_all_records(product, day_start, day_end, bbox)
        
        for day in self.daterange(start_date, end_date):
            day_start = day.strftime("%Y-%m-%dT00:00:00Z")
            day_end = day.strftime("%Y-%m-%dT23:59:59Z")
            args["file_paths"][day.strftime("%Y-%m-%d")] = get_all_records(product, day_start, day_end, bbox)
   
        # TODO: Missing parameters (bbox, band, etc)
        # TODO: Band filtering
        # TODO: Taggrenzen / Überschneidungen

        return args

    def calculate_storage_size(self, token, namespace, storage_class):
        ''' Calculates the needed storage of the node '''

        # TODO: Calculate storage size by file_sizes
        return "5Gi"

    def get_sub_nodes(self):
        ''' Returns the child nodes '''

        # TODO: Implement for filter if Core API integrates Array of imaginary
        return []
