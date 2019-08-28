from os import environ
import requests

class Airflow():
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

        request_url = self.dags_url + "/" + job_id + "/paused/" + str(unpause)
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

        job_url = self.dags_url + "/" + job_id + "/dag_runs"
        response = requests.get(job_url, headers=self.header, data=self.data)
        if response.status_code == 400:
            if 'not found' in response.json()['error']:
                dag_status = 'cancelled'
        else:
            dag_status = response.json()[0]['state']
        dag_status = dag_status.replace('success', 'finished')
            
        return dag_status
