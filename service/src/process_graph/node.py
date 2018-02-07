''' Process Node of the Process Graph'''

class Node():
    ''' Base class for processing nodes. '''

    def __init__(self, node_payload):
        self.node_id = node_payload["process_id"]

        self.input_nodes = []
        if "args" in node_payload:
            if "collections" in node_payload["args"]:
                for collection in node_payload["args"]["collections"]:

                    from service.src.process_graph.process_graph import ProcessGraph
                    node = ProcessGraph.parse_node(collection)

                    self.input_nodes.append(node)

            self.args = {}
            for key, value in node_payload["args"].items():
                if key is not "collections":
                    self.args[key] = value

    def execute(self):
        ''' Execute the processing node '''
        raise Exception("Not yet implemented!")
