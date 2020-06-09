import json
import os
from datetime import datetime
import shutil

import pytest
from nameko.testing.services import worker_factory
from nameko_sqlalchemy.database_session import Session

from jobs.models import Job
from jobs.service import JobService
from tests.mocks import MockedAirflowConnection, MockedDagWriter, MockedProcessesService, MockedFilesService, PG_OLD_REF


def load_json(filename: str) -> dict:
    json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', filename + '.json')
    with open(json_path) as f:
        return json.load(f)


def get_configured_job_service(db_session: Session) -> JobService:
    """
    Creates a JobService and adds a mocked ProcessService, mocked DagWriter and mocked AirflowConnection
    """
    job_service = worker_factory(JobService, db=db_session)
    job_service.processes_service = MockedProcessesService()  # needed to create / retrieve a process graph
    job_service.dag_writer = MockedDagWriter()  # needed to create a job
    job_service.airflow = MockedAirflowConnection()  # to update status and "trigger" dags
    job_service.files_service = MockedFilesService()  # needed to create / retrieve a process graph
    return job_service


def add_job(job_service: JobService, json_name: str = 'pg', user_id: str = 'test-user') -> str:
    """Gets a Job from a json and creates a Job in the JobService"""
    job_data = load_json(json_name)
    result = job_service.create(user_id=user_id, **job_data)
    assert result['status'] == 'success'
    assert os.path.isfile(os.path.join(os.environ['AIRFLOW_DAGS'], f'dag_{result["headers"]["OpenEO-Identifier"]}.py'))
    return result['headers']['OpenEO-Identifier']


def test_create_job(db_session: Session, set_job_data: pytest.fixture, dag_folder: pytest.fixture) -> None:
    job_service = worker_factory(JobService, db=db_session)
    job_service.processes_service = MockedProcessesService()
    job_service.dag_writer = MockedDagWriter()

    job_data = load_json('pg')
    # In this test: Job is added to database but dag file is not created (mocked away, as it happens in a separate pkg)
    result = job_service.create(user_id='test-user', **job_data)
    assert result['status'] == 'success'
    assert result['code'] == 201
    assert result['headers']['Location'].startswith('jobs/jb-')
    assert result['headers']['OpenEO-Identifier'].startswith('jb-')
    assert result['headers']['OpenEO-Identifier'] == result['headers']['Location'][5:]
    assert db_session.query(Job).filter(Job.user_id == 'test-user')\
        .filter(Job.id == result['headers']['OpenEO-Identifier']).count() == 1
    assert os.path.isfile(os.path.join(os.environ['AIRFLOW_DAGS'], f'dag_{result["headers"]["OpenEO-Identifier"]}.py'))


def test_get_job(db_session: Session, set_job_data: pytest.fixture, dag_folder: pytest.fixture) -> None:
    job_service = get_configured_job_service(db_session)
    job_id = add_job(job_service)

    # Get job
    result = job_service.get(user_id='test-user', job_id=job_id)
    assert result['status'] == 'success'
    # Datetime changes for each test -> cannot be compared to fixed value
    assert datetime.strptime(result['data'].pop('created'), '%Y-%m-%dT%H:%M:%S.%f')
    assert result['data'].pop('process') == PG_OLD_REF['data']['process_graph']
    assert result == {'code': 200,
                      'data': {
                          'id': job_id,
                          'budget': 1624.78,
                          'description': 'some description',
                          'plan': 'plan',
                          'status': 'created',
                          'title': 'evi_job_old'},
                      'status': 'success'}


def test_get_all_jobs(db_session: Session, set_job_data: pytest.fixture, dag_folder: pytest.fixture) -> None:
    job_service = get_configured_job_service(db_session)
    job_id = add_job(job_service)
    job_id_update = add_job(job_service, 'job_update_pg')

    # Get jobs
    result = job_service.get_all(user_id='test-user')
    assert result['status'] == 'success'
    # Datetime changes for each test -> cannot be compared to fixed value
    assert datetime.strptime(result['data']['jobs'][0].pop('created'), '%Y-%m-%dT%H:%M:%S.%f')
    assert datetime.strptime(result['data']['jobs'][1].pop('created'), '%Y-%m-%dT%H:%M:%S.%f')
    assert result == {'code': 200,
                      'data': {
                          'jobs': [{
                              'id': job_id,
                              'status': 'created',
                              'budget': 1624.78,
                              'description': 'some description',
                              'plan': 'plan',
                              'title': 'evi_job_old',
                          }, {
                              'id': job_id_update,
                              'status': 'created'
                          }],
                          'links': [],
                      },
                      'status': 'success',
                      }


def test_modify_job(db_session: Session, set_job_data: pytest.fixture, dag_folder: pytest.fixture) -> None:
    """Test modification of simple Job Attributes"""
    job_service = get_configured_job_service(db_session)
    job_id = add_job(job_service)
    initial_dag_file_time = os.path.getmtime(os.path.join(os.environ['AIRFLOW_DAGS'], f'dag_{job_id}.py'))

    job_args = {
        'title': 'New title',
        'description': 'New description',
        'plan': 'new plan',
        'budget': 1.28,
    }
    result = job_service.modify(user_id='test-user', job_id=job_id, **job_args)
    assert result == {'code': 204, 'status': 'success'}
    # Check dag file was not modified
    assert os.path.isfile(os.path.join(os.environ['AIRFLOW_DAGS'], f'dag_{job_id}.py'))
    assert initial_dag_file_time == os.path.getmtime(os.path.join(os.environ['AIRFLOW_DAGS'], f'dag_{job_id}.py'))

    job_args.update({'status': 'created'})
    result = job_service.get(user_id='test-user', job_id=job_id)
    assert result['status'] == 'success'
    assert datetime.strptime(result['data'].pop('created'), '%Y-%m-%dT%H:%M:%S.%f')
    assert result['data'].pop('id').startswith('jb-')
    assert result['data'].pop('process') == PG_OLD_REF['data']['process_graph']
    assert result == {'code': 200,
                      'data': job_args,
                      'status': 'success'}


def test_modify_job_pg(db_session: Session, set_job_data: pytest.fixture, dag_folder: pytest.fixture) -> None:
    """Test modification of a job's process graph"""
    job_service = get_configured_job_service(db_session)
    job_id = add_job(job_service)
    initial_dag_file_time = os.path.getmtime(os.path.join(os.environ['AIRFLOW_DAGS'], f'dag_{job_id}.py'))

    job_args: dict = {'process': {'process_graph': {}}}
    result = job_service.modify(user_id='test-user', job_id=job_id, **job_args)
    assert result == {'code': 204, 'status': 'success'}
    # Check dag file was updated
    assert os.path.isfile(os.path.join(os.environ['AIRFLOW_DAGS'], f'dag_{job_id}.py'))
    assert initial_dag_file_time < os.path.getmtime(os.path.join(os.environ['AIRFLOW_DAGS'], f'dag_{job_id}.py'))

    result = job_service.get(user_id='test-user', job_id=job_id)
    assert result['status'] == 'success'
    assert datetime.strptime(result['data'].pop('created'), '%Y-%m-%dT%H:%M:%S.%f')
    assert result['data'].pop('id').startswith('jb-')
    result['data'].pop('process')  # is returned from MockedProcessesService > always returns PG_OLD_REF
    assert result == {'code': 200,
                      'data': {'budget': 1624.78,
                               'description': 'some description',
                               'plan': 'plan',
                               'status': 'created',
                               'title': 'evi_job_old'},
                      'status': 'success'}


def test_delete_job(db_session: Session, set_job_data: pytest.fixture, dag_folder: pytest.fixture) -> None:
    job_service = get_configured_job_service(db_session)
    job_id = add_job(job_service)
    assert db_session.query(Job).filter(Job.user_id == 'test-user').filter(Job.id == job_id).count() == 1

    result = job_service.delete(user_id='test-user', job_id=job_id)
    assert result == {"status": "success", "code": 204}
    assert db_session.query(Job).filter(Job.user_id == 'test-user').filter(Job.id == job_id).count() == 0
    assert not os.path.isfile(os.path.join(os.environ['AIRFLOW_DAGS'], f'dag_{job_id}.py'))


def test_start_processing_job(db_session: Session, set_job_data: pytest.fixture, dag_folder: pytest.fixture) -> None:
    job_service = get_configured_job_service(db_session)
    job_id = add_job(job_service)

    result = job_service.process(user_id='test-user', job_id=job_id)
    assert result == {'code': 202, 'status': 'success'}


def test_start_processing_sync_job(db_session, set_job_data, dag_folder):
    job_service = get_configured_job_service(db_session)

    job_data = load_json('pg')
    _ = job_data.pop("title")
    _ = job_data.pop("description")

    result = job_service.process_sync(user_id='test-user', **job_data)
    
    assert result['status'] == 'success'
    assert 'result/sample-output.tif' in result['file']
    _ = result.pop('file')
    assert result == {'code': 200, 'status': 'success',
                      'headers': {'Content-Type': 'image/tiff', 'OpenEO-Costs': 0}
                      }
    
    # Clean up
    #shutil.rmtree("data/jb-12345")
    shutil.rmtree(os.environ['JOB_FOLDER'])
    shutil.rmtree(os.environ['SYNC_RESULTS_FOLDER'])
    
