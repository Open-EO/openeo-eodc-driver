"""
Tries to access all OpenEO jobs / batch processing endpoints

It does not do any checks automatically, you rather have to examine the return status and responses yourself.

To run this file a complete OpenEO backend has to be running under http://127.0.0.1:3000.
The basic auth credentials (USERNAME, PASSWORD) of a registered have to be stored as environment variables.
"""

import json
import os

import requests

backend_url = 'http://127.0.0.1:3000/v1.0'
basic_auth_url = backend_url + '/credentials/basic'
job_url = backend_url + '/jobs'
sync_job_url = backend_url + '/result'


def get_auth():
    auth_response = requests.get(basic_auth_url, auth=(os.environ.get('USERNAME'), os.environ.get('PASSWORD')))
    return {'Authorization': 'Bearer basic//' + auth_response.json()['access_token']}


def load_json(filename):
    json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', filename + '.json')
    with open(json_path) as f:
        return json.load(f)


def check_jobs():
    job = load_json('pg')
    response_create = requests.post(job_url, json=job, headers=get_auth())
    print(f"Create response: {response_create.status_code}")
    job_id = response_create.headers['Location'].split('jobs/')[-1]
    print(f'Job Id: {job_id}')

    response_get = requests.get(f'{job_url}/{job_id}', headers=get_auth())
    print(f"Get Full Response: {response_get.status_code}")

    response_get_all = requests.get(job_url, headers=get_auth())
    print(f"Get all response: {response_get_all.status_code}")

    job_update = load_json('job_update')
    response_patch = requests.patch(f'{job_url}/{job_id}', json=job_update, headers=get_auth())
    print(f"Patch Response: {response_patch.status_code}")

    response_process = requests.post(f'{job_url}/{job_id}/results', headers=get_auth())
    print(f"Process Response: {response_process.status_code}")

    response_delete = requests.delete(f'{job_url}/{job_id}', headers=get_auth())
    print(f"Delete Response: {response_delete.status_code}")

    response_process_sync = requests.post(sync_job_url, json=job, headers=get_auth())
    print(f"Process_sync response: {response_process_sync.status_code}")


if __name__ == '__main__':
    check_jobs()
