"""Tries to access all OpenEO job endpoints - A initial version of 'integration tests' for the jobs service..

To run them quiete some services need to be running - at least the gateway, RabbitMQ, the jobs, files and processes
service and the complete Airflow setup including webserver, scheduler, postgres, RabbitMQ and celery workers. Do not
forget to mount all required volumes / folders - for more details check the api docker-compose file - and provide
required environment variables.

Once the 'backend' is running some environment variable for this script need to be specified. In detail USERNAME,
PASSWORD, BACKEND_URL. To provide them you can copy the `sample_auth` file provided in this directory and add a USERNAME
PASSWORD combination existing on the backend. BACKEND_URL needs points to the public gateway url. Execute the copied
script to export the variables.

Then this script can be directly executed with
>>>python ./rest_calls.py

It will perform calls to all job service endpoints and print the status code. It does not do any checks automatically,
you rather have to examine the return status and responses yourself.
"""

import json
import os
from typing import Dict

import requests

backend_url = os.environ.get("BACKEND_URL")
if backend_url is None:
    raise OSError("Environment variable BACKEND_URL needs to be specified!")
basic_auth_url = backend_url + '/credentials/basic'
job_url = backend_url + '/jobs'
sync_job_url = backend_url + '/result'


def get_auth() -> Dict[str, str]:
    """Try to authenticate and return auth header for subsequent calls or None.

    The USERNAME and PASSWORD need to be set as environment variables.
    """
    auth_response = requests.get(basic_auth_url, auth=(os.environ.get('USERNAME'), os.environ.get('PASSWORD')))
    return {'Authorization': 'Bearer basic//' + auth_response.json()['access_token']}


def load_json(filename: str) -> dict:
    """Load json from the test data folder with the given filename."""
    json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', filename + '.json')
    with open(json_path) as f:
        return json.load(f)


def check_jobs() -> None:
    """Try to perform simple REST calls to all job service endpoints and print the return status code."""
    job = load_json('pg')
    response_create = requests.post(job_url, json=job, headers=get_auth())
    print(f"Create response: {response_create.status_code}")  # noqa T001
    job_id = response_create.headers['Location'].split('jobs/')[-1]
    print(f'Job Id: {job_id}')  # noqa T001

    response_get = requests.get(f'{job_url}/{job_id}', headers=get_auth())
    print(f"Get Full Response: {response_get.status_code}")  # noqa T001

    response_get_all = requests.get(job_url, headers=get_auth())
    print(f"Get all response: {response_get_all.status_code}")  # noqa T001

    job_update = load_json('job_update')
    response_patch = requests.patch(f'{job_url}/{job_id}', json=job_update, headers=get_auth())
    print(f"Patch Response: {response_patch.status_code}")  # noqa T001

    response_process = requests.post(f'{job_url}/{job_id}/results', headers=get_auth())
    print(f"Process Response: {response_process.status_code}")  # noqa T001

    response_delete = requests.delete(f'{job_url}/{job_id}', headers=get_auth())
    print(f"Delete Response: {response_delete.status_code}")  # noqa T001

    response_process_sync = requests.post(sync_job_url, json=job, headers=get_auth())
    print(f"Process_sync response: {response_process_sync.status_code}")  # noqa T001


if __name__ == '__main__':
    check_jobs()
