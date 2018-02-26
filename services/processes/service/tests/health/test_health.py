''' Unit Tests for Health Check '''

from service.tests.base import BaseTestCase
from service.api.utils import STATUS_CODE

class TestHealthCheck(BaseTestCase):
    ''' Test Class for Health Check '''

    def test_get_health(self):
        ''' Ensure that the health check is working '''

        response, data = self.send_get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Running!", data["message"])
        self.assertIn(STATUS_CODE[200], data["status"])
