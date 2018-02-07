''' Queries the /processes route '''

from requests import get, exceptions
from json import loads
from flask import current_app

def get_available_processes():
    ''' Returns all processes that are supported by the backend '''

    response = get(current_app.config["OPENEO_API"] + "/processes")
    response.raise_for_status()

    processes = loads(response.text)["data"]["processes"]

    process_ids = []
    for process in processes:
        process_ids.append(process["process_id"])

    return process_ids

def get_process_spec(process_id):
    ''' Returns the process description of a specific backend '''

    response = get(current_app.config["OPENEO_API"] + "/processes/" + process_id)
    response.raise_for_status()

    process = loads(response.text)["data"]["process"]

    return process

def get_available_products():
    ''' Returns all products that are supported by the backend '''

    response = get(current_app.config["OPENEO_API"] + "/data")
    response.raise_for_status()

    processes = loads(response.text)["data"]["processes"]

    product_ids = []
    for process in processes:
        process_ids.append(process["process_id"])

    return product_ids
