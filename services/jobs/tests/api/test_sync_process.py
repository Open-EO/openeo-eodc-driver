import pytest
from nameko_sqlalchemy.database_session import Session

from tests.utils import get_configured_job_service, get_random_user_id, load_json


@pytest.mark.usefixtures("set_job_data", "dag_folder")
class TestSyncJob:

    def test_start_processing_sync_job(self, db_session: Session) -> None:
        job_service = get_configured_job_service(db_session)
        user_id = get_random_user_id()

        job_data = load_json('pg')
        _ = job_data.pop("title")
        _ = job_data.pop("description")

        result = job_service.process_sync(user_id=user_id, **job_data)

        assert result['status'] == 'success'
        assert 'result/sample-output.tif' in result['file']
        _ = result.pop('file')
        assert result == {'code': 200, 'status': 'success',
                          'headers': {'Content-Type': 'image/tiff', 'OpenEO-Costs': 0}
                          }
