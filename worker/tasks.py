from os import environ
from worker.celery import app
from worker.process_graph.process_graph import ProcessGraph

def start_job_processing(job):
    ''' Executes the processes of a job '''

    # TODO: Own db table for process_graph  job -> Foreign Key
    # TODO: Get namespace and storage class of user
    # TODO: Get token of users service account
    # TODO: Get storage_class of user 
    token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJleGVjdXRpb24tZW52aXJvbm1lbnQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlY3JldC5uYW1lIjoicm9ib3QtdG9rZW4tdnc5OHQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoicm9ib3QiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiIzNjdjN2UxYS0xMTk5LTExZTgtYTc1Yi1mYTE2M2U4MzFkNjQiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6ZXhlY3V0aW9uLWVudmlyb25tZW50OnJvYm90In0.JZpNYER-rEvQrjpBI6NvJJjoo_RsRqsggIsKG7YOPIRM6OsEt6ZXvIycq5hQQzN44mUYsiym2d_GbcHcSvAjsuRDq0dEbYoRpC2pTxs0gNBEeSF-JI3SVoSwUwbdgk9znZbdNEM92qso33mYvc7w74AjU64rS6AvhFf7ox78IbEvazJBZxbpXqr8Ux5glapvyisQB3Zkx9AvI8o9FRpFocIOkv1QJjN5a2rSESsOrgsofqTpCdo2SiwQo0nAmKJ5AicEW4Q093PQnpNy-kNkBylOFPcsIFmjBkSyKCCDXaqZrw5maq1eECNJTgD8v_YJA5jDPtStO9dThm6gPFxujA"
    namespace = "execution-environment"
    storage_class = "storage-write"

    # Create and parse process graph
    process_graph = ProcessGraph(job["job_id"], job["task"])

    # Execute the process Graph
    result_pvc = process_graph.execute(token, namespace, storage_class)
