from os import environ
from celery import Celery
import datetime
from src.process_graph import ProcessGraph
from src.validation import validate_job

broker = "amqp://{user}:{password}@{host}:5672//"
broker.format(user=environ.get("RABBIT_MQ_USER"), 
              password=environ.get("RABBIT_MQ_PASSWORD"), 
              host=environ.get("RABBIT_MQ_HOST"))

print(broker)

celery = Celery("openeo_tasks", broker=broker)

@celery.task
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
        validate_job(job["task"])
        process_graph = ProcessGraph(job["job_id"], job["task"])
        process_graph.execute(token, namespace, storage_class)
    except Exception as exp:
        # TODO Exception Handling 
        print(exp)
