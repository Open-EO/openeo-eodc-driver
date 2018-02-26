from os import environ
from worker.celery import app
from worker.process_graph.process_graph import ProcessGraph

def start_job_processing(job):
    ''' Executes the processes of a job '''

    # TODO: Own db table for process_graph  job -> Foreign Key
    # TODO: Get namespace and storage class of user
    # TODO: Get token of users service account
    # TODO: Get storage_class of user 
    token = environ.get("SERVICEACCOUNT_TOKEN")
    namespace = environ.get("EXECUTION_NAMESPACE")
    storage_class = environ.get("STORAGE_CLASS")
    
    # Create and parse process graph
    process_graph = ProcessGraph(job["job_id"], job["task"])

    # Execute the process Graph
    result_pvc = process_graph.execute(token, namespace, storage_class)
