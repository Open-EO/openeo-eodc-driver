import json
import os

from processes.repository import construct_process_graph
from processes.schema import ProcessGraphShortSchema, ProcessGraphFullSchema


def test_process_graph_schema_short(data_path):
    with open(os.path.join(data_path, 'process_graph.json')) as f:
        process_graph_json = json.load(f)
    process_graph = construct_process_graph('user_id', process_graph_json)
    actual = ProcessGraphShortSchema().dump(process_graph).data

    with open(os.path.join(data_path, 'process_graph_short.json')) as f:
        ref = json.load(f)
    assert actual == ref


def test_process_graph_schema_full(data_path):
    with open(os.path.join(data_path, 'process_graph.json')) as f:
        process_graph_json = json.load(f)
    process_graph = construct_process_graph('user_id', process_graph_json)
    actual = ProcessGraphFullSchema().dump(process_graph).data

    with open(os.path.join(data_path, 'process_graph_full.json')) as f:
        ref = json.load(f)
    assert actual == ref
