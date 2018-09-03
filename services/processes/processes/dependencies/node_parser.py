from nameko.extensions import DependencyProvider


class NodesWrapper:
    def __init__(self):
        self.nodes = []
        # self.filters = {}

    def parse_process_graph(self, process_graph):
        # self.processes = processes
        self.parse_nodes(process_graph)

        # self.nodes = self.nodes[::-1]
        # self.nodes.append({
        #     "process_id": "prepare_for_download",
        #     "seq_num": len(self.nodes)
        # })
        
        # self.nodes.append(Task(job_id, "prepare_for_download", len(self.nodes), {"job_id": job_id}))

        return self.nodes

    # def extract_filter_args(self, filter_graph):
    #     if "process_id" in filter_graph:
    #         args = filter_graph["args"]
    #         imagery = args.pop("imagery")
    #         self.filters[filter_graph["process_id"]] = args
    #         self.extract_filter_args(imagery)
    #     elif "product_id" in filter_graph:
    #         self.filters["product"] = filter_graph["product_id"]

    def parse_nodes(self, node_graph):
        process_id = node_graph.pop("process_id")
        imagery = node_graph.pop("imagery", None)

        self.nodes.append({
            "process_id": process_id,
            "args": node_graph
        })

        if imagery:
            self.parse_nodes(imagery)


         # process_spec = [process for process in self.processes if process['name'] == process_id]
        # process_spec = process_spec[0]
        # if process_spec["p_type"] == "operation":
            

        #     self.nodes.append({
        #         "process_id": process_id,
        #         "seq_num": len(self.nodes),
        #         "args": node_graph
        #     })
        #     # self.nodes.append(
        #     #     Task(job_id, process_id, len(self.nodes), args))
        #     self.parse_nodes(job_id, imagery)
        # elif process_spec["p_type"] == "filter":
        #     self.extract_filter_args(node_graph)
        #     # process_id = self._filter_mapper[self.filters["product"]]

        #     self.nodes.append({
        #         "process_id": "get_data",
        #         "seq_num": len(self.nodes),
        #         "product_id": self.filters.pop("product", None),
        #         "args": self.filters
        #     })

            # self.nodes.append(
            #     Task(job_id, process_id, len(self.nodes), self.filters))


class NodeParser(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return NodesWrapper()
