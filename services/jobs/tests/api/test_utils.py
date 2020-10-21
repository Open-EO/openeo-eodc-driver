"""Test utility functions."""
from datetime import datetime, timedelta
from typing import Optional, Tuple

import pytest
from nameko_sqlalchemy.database_session import Session

from jobs.models import Job, JobStatus
from tests.utils import add_job, get_configured_job_service, get_random_user


@pytest.mark.usefixtures("job_folder", "dag_folder")
class TestUtils:
    """Test the utility function of the job service."""

    @pytest.mark.parametrize(("dag_status_prep", "dag_status_parallel", "ref_job_status"), (
        ((JobStatus.created, datetime.now()), (None, datetime.min), JobStatus.created),
        ((JobStatus.running, datetime.now()), (None, datetime.min), JobStatus.running),
        ((JobStatus.finished, datetime.now() - timedelta(minutes=1)), (JobStatus.running, datetime.now()),
         JobStatus.running),
        ((None, datetime.min), (None, datetime.min), JobStatus.created),
        ((JobStatus.error, datetime.now()), (JobStatus.finished, datetime.now() - timedelta(minutes=10)),
         JobStatus.error),
        ((JobStatus.finished, datetime.now() - timedelta(minutes=4)), (JobStatus.finished, datetime.now()),
         JobStatus.finished)
    ))
    def test_update_status_parallel(self, db_session: Session,
                                    dag_status_prep: Tuple[Optional[JobStatus], Optional[datetime]],
                                    dag_status_parallel: Tuple[Optional[JobStatus], Optional[datetime]],
                                    ref_job_status: JobStatus) -> None:
        """Test the update_status method.

        Different combinations for the two dags are provided and tested.
        """

        def check_dag_status_mock(dag_id: str) -> Tuple[Optional[JobStatus], Optional[datetime]]:
            """Return the dag_status depending on the dag_id."""
            if dag_id.endswith("prep"):
                return dag_status_prep
            if dag_id.endswith("parallel"):
                return dag_status_parallel
            return None, None

        job_service = get_configured_job_service(db_session, airflow=False)
        job_service.airflow.check_dag_status.side_effect = check_dag_status_mock
        user = get_random_user()
        job_id = add_job(job_service, user=user)
        assert db_session.query(Job).filter_by(id=job_id).first().status == JobStatus.created

        job_service._update_job_status(job_id=job_id)

        assert db_session.query(Job).filter_by(id=job_id).first().status == ref_job_status
