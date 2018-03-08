from __future__ import absolute_import, unicode_literals
from os import environ
from .celery import app
from .src.process_graph import ProcessGraph

@app.task
def start_job_processing(job):
    ''' Executes the processes of a job '''
    # TODO: Own db table for process_graph  job -> Foreign Key
    # TODO: Get namespace and storage class of user
    # TODO: Get token of users service account
    # TODO: Get storage_class of user

    token = environ.get("SERVICEACCOUNT_TOKEN")
    namespace = environ.get("EXECUTION_NAMESPACE")
    storage_class = environ.get("STORAGE_CLASS")

    try:
        process_graph = ProcessGraph(job["job_id"], job["task"])
        process_graph.execute(token, namespace, storage_class)
    except Exception as exp:
        # TODO Exception Handling 
        print(exp)
