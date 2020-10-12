"""A initial version of 'integration tests' for the data service.

To run them at least the gateway, RabbitMQ and the data service need to be up and running.

Also this script needs some environment variable. In detail USERNAME, PASSWORD, BACKEND_URL. To provide them you can
copy the `sample_auth` file provided in this directory and add a USERNAME PASSWORD combination existing on the backend.
BACKEND_URL needs points to the public gateway url. Execute the copied script to export the variables.

Then this script can be directly executed with
>>>python ./rest_calls.py

It will perform calls to all data service endpoints and print the status code. Besides the output no check are
performed.
"""

import os

import requests


def check_collections() -> None:
    """Try to perform simple REST calls to all data service endpoints."""
    backend_url = os.environ.get('BACKEND_URL')
    if backend_url is None:
        raise OSError("Environment variable BACKEND_URL needs to be specified!")
    basic_auth_url = backend_url + "/credentials/basic"
    collections_url = backend_url + "/collections"

    auth_response = requests.get(basic_auth_url, auth=(os.environ.get('USERNAME'), os.environ.get('PASSWORD')))
    auth_header = {'Authorization': 'Bearer basic//' + auth_response.json()['access_token']}

    response_get_all = requests.get(url=collections_url)
    assert response_get_all.ok
    response_post = requests.post(url=collections_url, headers=auth_header)
    assert response_post.ok
    response_get_all = requests.get(url=collections_url)
    assert response_get_all.ok
    response_get_single = requests.get(url=collections_url + "/s2a_prd_msil1c")
    assert response_get_single.ok


if __name__ == '__main__':
    check_collections()
