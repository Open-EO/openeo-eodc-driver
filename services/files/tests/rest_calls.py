"""Tries to access all OpenEO file endpoints - A initial version of 'integration tests' for the files service..

To run them at least the gateway, RabbitMQ and the files service need to be up and running. Remeber that the files
volume needs to be mounted to both the gateway and the files service and all environment variables are set correctly.

Once the 'backend' is running some environment variable for this script need to be specified. In detail USERNAME,
PASSWORD, BACKEND_URL. To provide them you can copy the `sample_auth` file provided in this directory and add a USERNAME
PASSWORD combination existing on the backend. BACKEND_URL needs points to the public gateway url. Execute the copied
script to export the variables.

Then this script can be directly executed with
>>>python ./rest_calls.py

It will perform calls to all file service endpoints and print the status code. It does not do any checks automatically,
you rather have to examine the return status and responses yourself.
"""

import os
from typing import Dict, Optional

import requests

backend_url = os.environ.get('BACKEND_URL')
if backend_url is None:
    raise OSError("Environment variable BACKEND_URL needs to be specified!")
files_url = backend_url + '/files'
file_single_url = files_url + '/folder1/upload.txt'
basic_auth_url = backend_url + '/credentials/basic'


def get_auth() -> Optional[Dict[str, str]]:
    """Try to authenticate and return auth header for subsequent calls or None.

    The USERNAME and PASSWORD need to be set as environment variables.
    """
    auth_response = requests.get(basic_auth_url, auth=(os.environ.get('USERNAME'), os.environ.get('PASSWORD')))
    if auth_response.ok:
        return {'Authorization': 'Bearer basic//' + auth_response.json()['access_token']}
    else:
        print(auth_response.text)  # noqa T001
        return None


def check_files() -> None:
    """Try to perform simple REST calls to all file service endpoints and print the return status code."""
    auth_header = get_auth()
    if not auth_header:
        return None
    upload_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'input', 'upload.txt')
    with open(upload_file) as f:
        auth_header["Content-Type"] = "application/octet-stream"
        response_upload = requests.put(file_single_url, headers=auth_header, data=f)
        auth_header.pop("Content-Type")
    print(f'Response upload: {response_upload.status_code}')  # noqa T001
    assert response_upload.status_code == 200

    response_get_all = requests.get(files_url, headers=auth_header)
    print(f'Response get all: {response_get_all.status_code}')  # noqa T001
    assert response_get_all.status_code == 200

    response_download = requests.get(file_single_url, headers=auth_header)
    print(f'Response download: {response_download.status_code}')  # noqa T001
    assert response_download.status_code == 200

    response_delete = requests.delete(file_single_url, headers=auth_header)
    print(f'Response delete: {response_delete.status_code}')  # noqa T001
    assert response_delete.status_code == 204


if __name__ == '__main__':
    check_files()
