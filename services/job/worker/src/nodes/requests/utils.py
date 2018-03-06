from requests import get, post
from json import loads

def send_get(path, headers={}, verify=False):
    response = get(path, headers=headers, verify=verify)
    response.raise_for_status()
    return loads(response.text)

def send_post(path, data, headers={}, verify=False):
    response = post(path, data=data, headers=headers, verify=verify)
    response.raise_for_status()
    return loads(response.text)