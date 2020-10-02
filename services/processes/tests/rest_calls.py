"""Tries to access all OpenEO processes endpoints - A initial version of 'integration tests' for the processess service.

To run them gateway, RabbitMQ and the processes and data service need to be up and running. Do not
forget to provide required environment variables.

Once the 'backend' is running some environment variable for this script need to be specified. In detail USERNAME,
PASSWORD, BACKEND_URL. To provide them you can copy the `sample_auth` file provided in this directory and add a USERNAME
PASSWORD combination existing on the backend. BACKEND_URL needs points to the public gateway url. Execute the copied
script to export the variables.

Then this script can be directly executed with
>>>python ./rest_calls.py

It will perform calls to all processes service endpoints and print the status code. It does not do any checks
automatically, you rather have to examine the return status and responses yourself.
"""

import json
import os
from typing import Dict

import requests

backend_url = os.environ.get('BACKEND_URL')
if backend_url is None:
    raise OSError("Environment variable BACKEND_URL needs to be specified!")
basic_auth_url = backend_url + '/credentials/basic'
process_url = backend_url + '/processes'
process_graph_url = backend_url + '/process_graphs'
process_graph_id_url = process_graph_url + '/user_cos'
validation_url = backend_url + '/validation'


def get_auth() -> Dict[str, str]:
    """Try to authenticate and return auth header for subsequent calls or None.

    The USERNAME and PASSWORD need to be set as environment variables.
    """
    auth_response = requests.get(basic_auth_url, auth=(os.environ.get('USERNAME'), os.environ.get('PASSWORD')))
    return {'Authorization': 'Bearer basic//' + auth_response.json()['access_token']}


def add_processes() -> None:
    """Try to add a list of predefined processes to the backend."""
    processes = ['absolute',
                 'add',
                 'add_dimension',
                 'aggregate_spatial',
                 'aggregate_spatial_binary',
                 'aggregate_temporal',
                 'all',
                 'and',
                 'any',
                 'apply',
                 'apply_dimension',
                 'apply_kernel',
                 'arccos',
                 'arcosh',
                 'arcsin',
                 'arctan',
                 'arctan2',
                 'array_apply',
                 'array_contains',
                 'array_element',
                 'array_filter',
                 'array_find',
                 'array_labels',
                 'arsinh',
                 'artanh',
                 'between',
                 'ceil',
                 'clip',
                 'cos',
                 'cosh',
                 'count',
                 'create_raster_cube',
                 'cummax',
                 'cummin',
                 'cumproduct',
                 'cumsum',
                 'debug',
                 'dimension_labels',
                 'divide',
                 'drop_dimension',
                 'e',
                 'eq',
                 'exp',
                 'extrema',
                 'filter_bands',
                 'filter_bbox',
                 'filter_labels',
                 'filter_spatial',
                 'filter_temporal',
                 'first',
                 'floor',
                 'gt',
                 'gte',
                 'if',
                 'int',
                 'is_nan',
                 'is_nodata',
                 'is_valid',
                 'last',
                 'linear_scale_range',
                 'ln',
                 'load_collection',
                 'load_result',
                 'load_uploaded_files',
                 'log',
                 'lt',
                 'lte',
                 'mask',
                 'mask_polygon',
                 'max',
                 'mean',
                 'median',
                 'merge_cubes',
                 'min',
                 'mod',
                 'multiply',
                 'ndvi',
                 'neq',
                 'normalized_difference',
                 'not',
                 'or',
                 'order',
                 'pi',
                 'power',
                 'product',
                 'quantiles',
                 'rearrange',
                 'reduce_dimension',
                 'reduce_dimension_binary',
                 'rename_dimension',
                 'rename_labels',
                 'resample_cube_spatial',
                 'resample_cube_temporal',
                 'resample_spatial',
                 'round',
                 'run_udf',
                 'run_udf_externally',
                 'save_result',
                 'sd',
                 'sgn',
                 'sin',
                 'sinh',
                 'sort',
                 'sqrt',
                 'subtract',
                 'sum',
                 'tan',
                 'tanh',
                 'text_begins',
                 'text_contains',
                 'text_ends',
                 'text_merge',
                 'trim_cube',
                 'variance',
                 'xor',
                 ]

    for proc in processes:
        response = requests.put(f'{backend_url}/processes/{proc}', headers=get_auth())
        print(f"{proc}: {response.status_code}")  # noqa T001

    response = requests.get(f'{backend_url}/processes')
    if response.status_code != 200:
        print('could not get predefined processes')  # noqa T001
        return

    all_predefined = json.loads(response.content)
    for actual in all_predefined['processes']:
        ref = requests.get(f'https://raw.githubusercontent.com/Open-EO/openeo-processes/1.0.0/{actual["id"]}.json')
        ref_content: dict = json.loads(ref.content)
        wrong = {key: {
            'actual': actual[key],
            'ref': ref_content[key]
        } for key in ref_content.keys()
            if not (key in ref_content and ref_content[key] == actual[key])}
        print(wrong)  # noqa T001


def run_process_graphs() -> None:
    """Try to perform simple REST calls to all process service endpoints and print the return status code."""
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'process_graph.json')
    with open(json_path) as f:
        process_graph = json.load(f)

    get_all_pre_response = requests.get(process_url)
    print(f"Get all predefined request: {get_all_pre_response.status_code}")  # noqa T001

    get_all_user_response = requests.get(process_graph_url, headers=get_auth())
    print(f"Get all request: {get_all_user_response.status_code}")  # noqa T001

    put_response = requests.put(process_graph_id_url, json=process_graph, headers=get_auth())
    print(f"Put request: {put_response.status_code}")  # noqa T001

    get_all_user_response = requests.get(process_graph_url, headers=get_auth())
    print(f"Get all request: {get_all_user_response.status_code}")  # noqa T001

    get_response = requests.get(process_graph_id_url, headers=get_auth())
    print(f"Get request: {get_response.status_code}")  # noqa T001

    delete_response = requests.delete(process_graph_id_url, headers=get_auth())
    print(f"Delete request: {delete_response.status_code}")  # noqa T001

    validation_response = requests.post(validation_url, json=process_graph, headers=get_auth())
    print(f"Validation request: {validation_response.status_code}")  # noqa T001


if __name__ == '__main__':
    run_process_graphs()
