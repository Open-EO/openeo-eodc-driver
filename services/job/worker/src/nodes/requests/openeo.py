from os import environ
from re import match
from .utils import send_get

OPENEO_API_HOST = environ.get("OPENEO_API_HOST")
if not match(r"^http(s)?:\/\/", OPENEO_API_HOST):
    OPENEO_API_HOST = "http://" + OPENEO_API_HOST

def get_single(host, path, identifier, option=None):
    if not option:
        url = "{0}/{1}/{2}".format(OPENEO_API_HOST, path, identifier)
    else:
        url = "{0}/{1}/{2}/{3}".format(OPENEO_API_HOST, path, identifier, option)
    return send_get(url)

def get_all(host, path, identifier):
    url = "{0}/{1}".format(OPENEO_API_HOST, path)
    response = send_get(url)

    all_items = []
    for item in response:
        all_items.append(item[identifier])
    
    return all_items