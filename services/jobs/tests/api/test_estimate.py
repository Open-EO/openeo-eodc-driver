from nameko_sqlalchemy.database_session import Session

from tests.utils import get_configured_job_service


class TestEstimateJob:

    def test_default_estimates(self, db_session: Session) -> None:
        job_service = get_configured_job_service(db_session)
        result = job_service.estimate(user_id='test-user', job_id='test_job')
        assert result == {
            "status": "success",
            "code": 200,
            "data": {
                "costs": 0,
            },
        }
