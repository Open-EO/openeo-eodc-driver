from nameko.extensions import DependencyProvider


class NodesWrapper:
    def __init__(self):
        self.nodes = []
        self.filters = {
            "data_id": None,
            "time": None,
            "bands": None,
            "extent": None,
            "derived_from": None,
            "license": None
        }

    def parse_process_graph(self, process_graph: dict, processes: list) -> list:
        self.parse_nodes(process_graph, processes)
        return self.nodes

    def parse_filter(self, process_id: str, filter_args: dict):

        # TODO: Not a good solution: Has to be adapted as soon as
        # the processes are better specified
        # TODO: Bands can be name, band_id, wavelengths as str or list
        if process_id == "get_collection":
            for key, value in filter_args.items():
                self.filters[key] = value
        if process_id == "filter_bands":
            self.filters["bands"] = filter_args
        if process_id == "filter_bbox":
            self.filters["extent"] = filter_args
        if process_id == "filter_daterange":
            self.filters["time"] = filter_args


    def parse_nodes(self, node_graph: dict, processes: list):
        process_id = node_graph.pop("process_id")
        imagery = node_graph.pop("imagery", None)

        process_spec = [p for p in processes if p['name'] == process_id]
        if process_spec[0]["p_type"] == "filter":
            self.parse_filter(process_id, node_graph)
        else:
            self.nodes.append({
                "process_id": process_id,
                "args": node_graph
            })

        if imagery:
            self.parse_nodes(imagery, processes)


class NodeParser(DependencyProvider):
    def get_dependency(self, worker_ctx):
        return NodesWrapper()
