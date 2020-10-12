"""Utility functions used in the tests."""
import json
import os
from typing import Any, Dict
from uuid import uuid4

from nameko.testing.services import worker_factory
from nameko_sqlalchemy.database_session import Session

from jobs.models import Job
from jobs.service import JobService
from .mocks import MockedAirflowConnection, MockedDagHandler, MockedDagWriter, MockedFilesService, \
    MockedProcessesService


def load_json(filename: str) -> dict:
    """Load a json file with the given filename from the test data folder."""
    json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', filename + '.json')
    with open(json_path) as f:
        return json.load(f)


def get_configured_job_service(db_session: Session, processes: bool = True, dag_writer: bool = True,
                               airflow: bool = True, files: bool = True, dag_handler: bool = True) -> JobService:
    """Create a JobService and add mockes as required.

    By default all available mocks are added.
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
    if dag_handler:
        job_service.dag_handler = MockedDagHandler()
    return job_service


def add_job(job_service: JobService, user: Dict[str, Any], json_name: str = 'pg') -> str:
    """Get a job definition from a json and create the corresponding job in the JobService."""
    job_data = load_json(json_name)
    result = job_service.create(user=user, **job_data)
    assert result['status'] == 'success'
    return result['headers']['OpenEO-Identifier']


def get_uuid_str() -> str:
    """Return a randum uuid as string."""
    return str(uuid4())


def get_random_user_id() -> str:
    """Return a random user id."""
    return get_uuid_str()


def get_random_job_id() -> str:
    """Return a random job id."""
    return get_uuid_str()


def get_random_user() -> Dict[str, Any]:
    """Return a basic random user."""
    return {
        "id": get_random_user_id(),
    }


def get_pg_id_from_job_id(db_session: Session, job_id: str) -> str:
    """Return the process graph id of the given job."""
    return db_session.query(Job.process_graph_id).filter_by(id=job_id).first()
