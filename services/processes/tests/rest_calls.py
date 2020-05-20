"""
Tries to access all OpenEO process / process graph endpoints

It does not do any checks automatically, you rather have to examine the return status and responses yourself.

To run this file a complete OpenEO backend has to be running under http://127.0.0.1:3000.
The basic auth credentials (USERNAME, PASSWORD) of a registered have to be stored as environment variables.
"""

import json
import os

import requests

backend_url = 'http://127.0.0.1:3000/v1.0'
basic_auth_url = backend_url + '/credentials/basic'
process_url = backend_url + '/processes'
process_graph_url = backend_url + '/process_graphs'
process_graph_id_url = process_graph_url + '/user_cos'
validation_url = backend_url + '/validation'


def get_auth():
    auth_response = requests.get(basic_auth_url, auth=(os.environ.get('USERNAME'), os.environ.get('PASSWORD')))
    return {'Authorization': 'Bearer basic//' + auth_response.json()['access_token']}


def add_processes():
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
        print(f"{proc}: {response.status_code}")

    response = requests.get(f'{backend_url}/processes')
    if response.status_code != 200:
        print('could not get predefined processes')
        return

    all_predefined = json.loads(response.content)
    for actual in all_predefined['processes']:
        ref = requests.get(f'https://raw.githubusercontent.com/Open-EO/openeo-processes/1.0.0-rc.1/{actual["id"]}.json')
        ref = json.loads(ref.content)
        wrong = {key: {'actual': actual[key], 'ref': ref[key]} for key in ref.keys() if not(key in ref and ref[key] == actual[key])}
        print(wrong)


def run_process_graphs():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'process_graph.json')
    with open(json_path) as f:
        process_graph = json.load(f)

    get_all_pre_response = requests.get(process_url)
    print(f"Get all predefined request: {get_all_pre_response.status_code}")

    get_all_user_response = requests.get(process_graph_url, headers=get_auth())
    print(f"Get all request: {get_all_user_response.status_code}")

    put_response = requests.put(process_graph_id_url, json=process_graph, headers=get_auth())
    print(f"Put request: {put_response.status_code}")

    get_all_user_response = requests.get(process_graph_url, headers=get_auth())
    print(f"Get all request: {get_all_user_response.status_code}")

    get_response = requests.get(process_graph_id_url, headers=get_auth())
    print(f"Get request: {get_response.status_code}")

    delete_response = requests.delete(process_graph_id_url, headers=get_auth())
    print(f"Delete request: {delete_response.status_code}")

    validation_response = requests.post(validation_url, json=process_graph, headers=get_auth())
    print(f"Validation request: {validation_response.status_code}")


if __name__ == '__main__':
    run_process_graphs()
