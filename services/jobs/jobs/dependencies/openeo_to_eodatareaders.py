from openeo_pg_parser_python.translate_process_graph import translate_graph

try:
    from map_processes import map_process
except:
    from .map_processes import map_process


def openeo_to_eodatareaders(process_graph_json, job_data):
    """
    
    """

    graph = translate_graph(process_graph_json)
    nodes = []
    for node_id in graph.nodes:            
        # Check if this node contains a callback
        reducer_name = None
        reducer_dimension = None
        node_dependencies = None
        if 'reducer' in graph.nodes[node_id].graph['parameters'].keys():
            if 'callback'in graph.nodes[node_id].graph['parameters']['reducer'].keys():
                callback_pg = graph.nodes[node_id].graph['parameters']['reducer']['callback']
                if 'process_id' in callback_pg:
                    # Callback is using an existing process
                    reducer_name = graph.nodes[graph.nodes[node_id].graph['parameters']['reducer']['from_node']].graph['process_id']
                    reducer_dimension = graph.nodes[node_id].graph['parameters']['dimension']
            elif 'from_node' in graph.nodes[node_id].graph['parameters']['reducer'].keys():
                # Callback is itself a process graph
                node_dependencies = [graph.nodes[node_id].graph['parameters']['reducer']['from_node']]
        
        if graph.nodes[node_id].graph['process_id'] == "reduce":
            reducer_name = graph.nodes[graph.nodes[node_id].graph['parameters']['reducer']['from_node']].graph['process_id']
            reducer_dimension = graph.nodes[node_id].graph['parameters']['dimension']
        
        # Convert openeo process to eoDataReaders syntax
        # Check if this node comes from a reduce node
        else:
            for node_edge in graph.nodes[node_id].edges:
                # Pass dimension paramer to children of callback
                if node_edge.node_ids[0] == node_id and node_edge.name == 'callback':
                    parent_node_graph = graph.nodes[node_edge.node_ids[1]].graph
                    if 'dimension' in parent_node_graph['parameters'].keys():
                        reducer_dimension = parent_node_graph['parameters']['dimension']
                        reducer_name = graph.nodes[node_id].graph['process_id']
        
        # TODO: dimension names should be available to users via dube metadata
        if reducer_dimension:
            reducer_dimension = reducer_dimension.replace('spectral', 'band')
            reducer_dimension = reducer_dimension.replace('temporal', 'time')
        params, filepaths = map_process(
                                        graph.nodes[node_id].graph,
                                        graph.nodes[node_id].name,
                                        graph.nodes[node_id].id,
                                        job_data,
                                        reducer_name=reducer_name,
                                        reducer_dimension=reducer_dimension
                                        )
        # Get node dependencies
        if not node_dependencies and graph.nodes[node_id].dependencies:
            node_dependencies = []
            for dependency in graph.nodes[node_id].dependencies:
                if 'callback' not in dependency.id:
                    node_dependencies.append(dependency.id)
            if reducer_dimension != 'time':
                for k, item in enumerate(params):
                    if item['name'] == 'reduce':
                        params[k]['per_file'] = 'True'
        
        # Add to nodes list
        nodes.append((graph.nodes[node_id].id, params, filepaths, node_dependencies))
        
    return nodes, graph
