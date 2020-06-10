import json
import os

import requests


def send_udf_service_request(json_dat: dict, url: str):
    response = requests.post(url=url, json=json_dat, headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        return response.text
    return None


def read_json_file(filepath: str):
    with open(filepath) as f:
        return json.load(f)


def run():
    url_python = "http://localhost:5051/udf"
    url_r = "http://localhost:5052/udf"
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples", "hypercube_try.json")
    dat = read_json_file(path)
    response = send_udf_service_request(json_dat=dat, url=url_python)
    print(response)


if __name__ == '__main__':
    run()
