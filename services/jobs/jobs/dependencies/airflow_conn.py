from os import environ
import requests


from ..models import JobStatus


job_status_mapper = {
    "submitted": JobStatus.created,
    "created": JobStatus.created,
    "queued": JobStatus.queued,
    "running": JobStatus.running,
    "cancelled": JobStatus.canceled,
    "finished": JobStatus.finished,
    "success": JobStatus.finished,
    "error": JobStatus.error
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

        response = requests.get(self.api_url + "/test")

        return response

    def unpause_dag(self, job_id, unpause=True):
        """
        Pause/unpause DAG
        """

        request_url = self.dags_url + "/" + job_id + "/paused/" + str(not unpause)
        response = requests.get(request_url, headers=self.header, data=self.data)

        return response


    def trigger_dag(self, job_id):
        """
        Trigger airflow DAG (only works if it is unpaused already)
        """

        job_url = self.dags_url + "/" + job_id + "/dag_runs"
        response = requests.post(job_url, headers=self.header, data=self.data)

        return response

    def check_dag_status(self, job_id):
        """
        Check status of airflow DAG
        """
        dag_status = JobStatus.created

        job_url = self.dags_url + "/" + job_id + "/dag_runs"
        response = requests.get(job_url, headers=self.header, data=self.data)
        if response.status_code == 400:
            if 'not found' in response.json()['error']:
                dag_status = JobStatus.canceled
            else:
                dag_status = JobStatus.error
        else:
            if response.json():
                state = response.json()[0]['state']
                if state in job_status_mapper:
                    dag_status = job_status_mapper[state]

        return dag_status
