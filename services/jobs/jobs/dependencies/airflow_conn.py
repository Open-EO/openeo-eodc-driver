"""Handles REST connection to Airflow service."""

from datetime import datetime
from typing import Optional, Tuple

import requests
from dynaconf import settings
from nameko.extensions import DependencyProvider

from ..models import JobStatus

airflow_job_status_mapper = {
    "running": JobStatus.running,
    "success": JobStatus.finished,
    "failed": JobStatus.error
}
"""Simple dictionary to map from a str to the corresponding JobStatus enum."""


class AirflowRestConnection:
    """Handles REST requests to the Airflow webserver."""

    def __init__(self, airflow_base_url: str) -> None:
        """Initialize Airflow REST connection service."""
        self.header = {'Cache-Control': 'no-cache ', 'content-type': 'application/json'}
        self.data = '{}'
        self.api_url = f"{airflow_base_url}/api/experimental"
        self.dag_url = f"{self.api_url}/dags"

    def unpause_dag(self, dag_id: str, unpause: bool = True) -> bool:
        """Pause/unpause dag and return whether this was successful."""
        request_url = f"{self.dag_url}/{dag_id}/paused/{str(not unpause)}"
        response = requests.get(request_url, headers=self.header, data=self.data)
        # NB It may take 1-2 seconds before the DAG has the attribute "is_paused" set
        while not response.ok:
            response = requests.get(request_url, headers=self.header, data=self.data)
        return response.ok

    def trigger_dag(self, dag_id: str) -> bool:
        """Trigger given airflow dag and return whether this was successful."""
        _ = self.unpause_dag(dag_id)
        job_url = f"{self.dag_url}/{dag_id}/dag_runs"
        response = requests.post(job_url, headers=self.header, data=self.data)
        return response.ok

    def check_dag_status(self, dag_id: str) -> Tuple[Optional[JobStatus], Optional[datetime]]:
        """Check status of airflow dag and return it together with the last execution date.

        Returns:
            A Tuple containing the current dag status and the last execution date. If the REST request to the Airflow
            service fails None, None is returned. If the dag has not been executed created, None is returned.
        """
        dag_status = None
        execution_date = datetime.min

        job_url = f"{self.dag_url}/{dag_id}/dag_runs"
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

    def delete_dag(self, dag_id: str) -> bool:
        """Delete the dag from Airflow with the given id an return whether this was successful."""
        job_url = f"{self.dag_url}/{dag_id}"
        response = requests.delete(job_url)
        return response.status_code == 200


class AirflowRestConnectionProvider(DependencyProvider):
    """This is the DependencyProvider of the AirflowRestConnection."""

    def get_dependency(self, worker_ctx: object) -> AirflowRestConnection:
        """Return the instantiated object that is injected to a service worker.

        Args:
            worker_ctx: The service worker.

        Returns:
            AirflowRestConnection: The instantiated AirflowRestConnection object.
        """
        return AirflowRestConnection(
            airflow_base_url=settings.AIRFLOW_HOST
        )
