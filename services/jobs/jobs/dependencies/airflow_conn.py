from os import environ
from typing import Optional

import requests


from ..models import JobStatus


airflow_job_status_mapper = {
    "running": JobStatus.running,
    "success": JobStatus.finished,
    "failed": JobStatus.error
}


class Airflow:
    """

    """

    def __init__(self):
        """
        
        """

        self.api_url = environ.get('AIRFLOW_HOST') + "/api/experimental"
        self.dags_url = environ.get('AIRFLOW_HOST') + "/api/experimental/dags"
        self.header = {'Cache-Control': 'no-cache ', 'content-type': 'application/json'}
        self.data = '{}'

    def check_api(self):
        """
        
        """
        return requests.get(self.api_url + "/test")

    def unpause_dag(self, job_id: str, unpause: bool = True) -> bool:
        """
        Pause/unpause DAG
        """
        request_url = f"{self.dags_url}/{job_id}/paused/{str(not unpause)}"
        response = requests.get(request_url, headers=self.header, data=self.data)
        return response.status_code == 200

    def trigger_dag(self, job_id: str) -> bool:
        """
        Trigger airflow DAG (only works if it is unpaused already)
        """
        self.unpause_dag(job_id)
        job_url = f"{self.dags_url}/{job_id}/dag_runs"
        response = requests.post(job_url, headers=self.header, data=self.data)
        return response.status_code == 200

    def check_dag_status(self, job_id: str) -> Optional[JobStatus]:
        """
        Check status of airflow DAG
        """
        dag_status = None

        job_url = f"{self.dags_url}/{job_id}/dag_runs"
        response = requests.get(job_url, headers=self.header, data=self.data)
        if response.status_code == 200:
            if not response.json():
                # empty list is returned > no dag run, only created
                dag_status = JobStatus.created
            else:
                state = response.json()[-1]['state']  # TODO shouldn't this be the max?
                dag_status = airflow_job_status_mapper[state]

        return dag_status

    def delete_dag(self, job_id: str) -> bool:
        """
        Delete the dag with the given id.
        """
        job_url = f"{self.dags_url}/{job_id}"
        response = requests.delete(job_url)
        return response.status_code == 200
