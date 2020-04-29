"""
Tries to access all OpenEO file endpoints

It does not do any checks automatically, you rather have to examine the return status and responses yourself.

To run this file a complete OpenEO backend has to be running under http://127.0.0.1:3000.
The basic auth credentials (USERNAME, PASSWORD) of a registered have to be stored as environment variables.
"""

import os

import requests

backend_url = 'http://127.0.0.1:3000'
files_url = backend_url + '/files'
file_single_url = files_url + '/folder1/upload.txt'
basic_auth_url = backend_url + '/credentials/basic'


def get_auth():
    auth_response = requests.get(basic_auth_url, auth=(os.environ.get('USERNAME'), os.environ.get('PASSWORD')))
    return {'Authorization': 'Bearer basic//' + auth_response.json()['access_token']}


def check_files():
    auth_header = get_auth()
    upload_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'input', 'upload.txt')
    with open(upload_file) as f:
        auth_header["Content-Type"] = "application/octet-stream"
        response_upload = requests.put(file_single_url, headers=auth_header, data=f)
        auth_header.pop("Content-Type")
    print(f'Response upload: {response_upload.status_code}')
    assert response_upload.status_code == 200

    response_get_all = requests.get(files_url, headers=get_auth())
    print(f'Response get all: {response_get_all.status_code}')
    assert response_get_all.status_code == 200

    response_download = requests.get(file_single_url, headers=get_auth())
    print(f'Response download: {response_download.status_code}')
    assert response_download.status_code == 200

    response_delete = requests.delete(file_single_url, headers=get_auth())
    print(f'Response delete: {response_delete.status_code}')
    assert response_delete.status_code == 204


if __name__ == '__main__':
    check_files()
