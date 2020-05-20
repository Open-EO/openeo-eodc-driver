from datetime import datetime
from os import environ
from typing import Optional, Tuple

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
        self.header = {'Cache-Control': 'no-cache ', 'content-type': 'application/json'}
        self.data = '{}'

    def get_api_url(self):
        return environ.get('AIRFLOW_HOST') + "/api/experimental"

    def get_dags_url(self):
        return environ.get('AIRFLOW_HOST') + "/api/experimental/dags"

    def check_api(self):
        """
        
        """
        return requests.get(self.get_api_url() + "/test")

    def unpause_dag(self, job_id: str, unpause: bool = True) -> bool:
        """
        Pause/unpause DAG
        """
        request_url = f"{self.get_dags_url()}/{job_id}/paused/{str(not unpause)}"
        response = requests.get(request_url, headers=self.header, data=self.data)
        return response.status_code == 200

    def trigger_dag(self, job_id: str) -> bool:
        """
        Trigger airflow DAG (only works if it is unpaused already)
        """
        self.unpause_dag(job_id)
        job_url = f"{self.get_dags_url()}/{job_id}/dag_runs"
        response = requests.post(job_url, headers=self.header, data=self.data)
        return response.status_code == 200

    def check_dag_status(self, job_id: str) -> Tuple[Optional[JobStatus], Optional[datetime]]:
        """
        Check status of airflow DAG
        """
        dag_status = None
        execution_date = None

        job_url = f"{self.get_dags_url()}/{job_id}/dag_runs"
        response = requests.get(job_url, headers=self.header, data=self.data)
        if response.status_code == 200:
            if not response.json():
                # empty list is returned > no dag run, only created
                dag_status = JobStatus.created
            else:
                last_run = response.json()[-1]
                dag_status = airflow_job_status_mapper[last_run["state"]]
                try:
                    execution_date = datetime.strptime(last_run["execution_date"], "%Y-%m-%dT%H:%M:%S+00:00")
                except ValueError:
                    execution_date = datetime.strptime(last_run["execution_date"], "%Y-%m-%dT%H:%M:%S.%f+00:00")

        return dag_status, execution_date

    def delete_dag(self, job_id: str) -> bool:
        """
        Delete the dag with the given id.
        """
        job_url = f"{self.get_dags_url()}/{job_id}"
        response = requests.delete(job_url)
        return response.status_code == 200
