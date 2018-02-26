''' Queries the openEO API '''

from requests import get, exceptions
from json import loads
from flask import current_app

def get_available_processes(auth):
    ''' Returns all processes that are supported by the backend '''

    response = get(current_app.config["OPENEO_API"] + "/processes", headers=auth)
    response.raise_for_status()

    processes = loads(response.text)

    process_ids = []
    for process in processes:
        process_ids.append(process["process_id"])

    return process_ids

def get_process_spec(process_id, auth):
    ''' Returns the process description of a specific backend '''

    response = get(current_app.config["OPENEO_API"] + "/processes/" + process_id, headers=auth)
    response.raise_for_status()

    process = loads(response.text)

    return process

def get_available_products(auth):
    ''' Returns all products that are supported by the backend '''

    response = get(current_app.config["OPENEO_API"] + "/data", headers=auth)
    response.raise_for_status()

    products = loads(response.text)

    product_ids = []
    for product in products:
        product_ids.append(product["product_id"])

    return product_ids