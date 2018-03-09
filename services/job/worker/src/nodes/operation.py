''' Operation Node of Process Graph '''

from .node import Node

class Operation(Node):
    ''' Operation node for perform operations on filtered data '''

    def __init__(self, graph_id, operation_payload, operation_spec):
        super().__init__(graph_id)

        self.operation_id = operation_payload["process_id"].lower().replace("_", "-")
        self.spec = operation_spec

        self.args = {}
        self.input_nodes = []
        for key, value in operation_payload["args"].items():
            if key == "imagery":
                input_node = Node.parse_node(graph_id, value)
                self.input_nodes.append(input_node)
            else:
                self.args[key] = value

    def get_process_id(self):
        ''' Returns the process_id '''
        return self.operation_id
    
    def get_arguments(self):
        ''' Returns the arguments '''
        return self.args
    
    def calculate_storage_size(self, token, namespace, storage_class):
        ''' Calculates the needed storage of the node '''

        # TODO: Calculate storage size by input pvcs
        return "5Gi"

    def get_sub_nodes(self):
        ''' Returns the child nodes '''
        return self.input_nodes
