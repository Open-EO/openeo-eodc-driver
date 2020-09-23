"""Provide base test class."""
from typing import Any, Callable

from nameko_sqlalchemy.database_session import Session

from jobs.dependencies.dag_handler import DagHandler
from jobs.service import JobService
from .exceptions import get_missing_resource_service_exception, get_not_authorized_service_exception
from ..utils import add_job, get_configured_job_service, get_random_job_id, get_random_user


class BaseCase:
    """Base test class to be inherited from by other test classes."""

    dag_handler = DagHandler()

    def get_method(self, service: JobService, method: str) -> Callable:
        """Return service method corresponding to a given string."""
        mapper = {
            "get": service.get,
            "modify": service.modify,
            "delete": service.delete,
            "process": service.process,
            "get_results": service.get_results,
        }
        if method not in mapper:
            raise NotImplementedError(f"The method {method} is currently not supported")
        return mapper[method]

    def test_not_existing_job(self, db_session: Session, method: str, **kwargs: Any) -> None:
        """Check trying to access a non existing job throws the expected error.

        Args:
            db_session: Database session.
            method: Which method to call with a non-existing job identifier.
            kwargs: Additional keyword arguments which need to be supplied to the given method.
        """
        job_service = get_configured_job_service(db_session)
        user = get_random_user()
        job_id = get_random_job_id()

        result = self.get_method(job_service, method)(user=user, job_id=job_id, **kwargs)
        assert result == get_missing_resource_service_exception(user_id=user["id"], job_id=job_id)

    def test_not_authorized_for_job(self, db_session: Session, method: str, **kwargs: Any) -> None:
        """Check trying to access a job of another user throws the expected error.

        Args:
            db_session: Database session.
            method: Which method to call as not authorized user.
            kwargs: Additional keyword arguments which need to be supplied to the given method.
        """
        job_service = get_configured_job_service(db_session)
        user = get_random_user()
        job_id = add_job(job_service, user=user)
        other_user = get_random_user()

        result = self.get_method(job_service, method)(user=other_user, job_id=job_id, **kwargs)
        assert result == get_not_authorized_service_exception(user_id=other_user["id"], job_id=job_id)
