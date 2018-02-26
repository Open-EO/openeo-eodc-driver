import json
from service.tests.base import BaseTestCase


class TestHealthCheck(BaseTestCase):
    ''' Test for health check. '''

    def test_get_pong(self):
        ''' Ensure the health check is working. '''

        response, data = self.send_get("/ping")

        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])