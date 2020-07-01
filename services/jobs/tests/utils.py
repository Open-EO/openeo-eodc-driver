import json
import os
from uuid import uuid4

from dynaconf import settings
from nameko.testing.services import worker_factory
from nameko_sqlalchemy.database_session import Session

from jobs.models import Job
from jobs.service import JobService
from .mocks import MockedAirflowConnection, MockedDagWriter, MockedFilesService, MockedProcessesService


def load_json(filename: str) -> dict:
    json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', filename + '.json')
    with open(json_path) as f:
        return json.load(f)


def get_configured_job_service(db_session: Session, processes: bool = True, dag_writer: bool = True,
                               airflow: bool = True, files: bool = True) -> JobService:
    """
    Creates a JobService and adds a mocked ProcessService, mocked DagWriter and mocked AirflowConnection
    """
    job_service = worker_factory(JobService, db=db_session)
    if processes:
        job_service.processes_service = MockedProcessesService()  # needed to create / retrieve a process graph
    if dag_writer:
        job_service.dag_writer = MockedDagWriter()  # needed to create a job
    if airflow:
        job_service.airflow = MockedAirflowConnection()  # to update status and "trigger" dags
    if files:
        job_service.files_service = MockedFilesService()  # needed to create / retrieve a process graph
    return job_service


def get_dag_path(dag_id: str) -> str:
    return os.path.join(settings.AIRFLOW_DAGS, f'dag_{dag_id}.py')


def add_job(job_service: JobService, user_id: str, json_name: str = 'pg') -> str:
    """Gets a Job from a json and creates a Job in the JobService"""
    job_data = load_json(json_name)
    result = job_service.create(user_id=user_id, **job_data)
    assert result['status'] == 'success'
    assert os.path.isfile(get_dag_path(result["headers"]["OpenEO-Identifier"]))
    return result['headers']['OpenEO-Identifier']


def get_uuid_str() -> str:
    return str(uuid4())


def get_random_user_id() -> str:
    return get_uuid_str()


def get_random_job_id() -> str:
    return get_uuid_str()


def get_pg_id_from_job_id(db_session: Session, job_id: str) -> str:
    return db_session.query(Job.process_graph_id).filter_by(id=job_id).first()
