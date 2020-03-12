import json
import os

from processes.models import ProcessGraph, Parameter, Return
from processes.repository import construct_process_graph


def test_construct_process_graph(data_path):
    with open(os.path.join(data_path, 'process_graph.json')) as f:
        process_graph_json = json.load(f)

    process_graph = construct_process_graph('user_id', process_graph_json)
    assert isinstance(process_graph, ProcessGraph)
    assert all([isinstance(process_graph.parameters[i], Parameter) for i in range(0, 2)])
    assert isinstance(process_graph.returns, Return)
