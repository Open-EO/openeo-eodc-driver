''' Tests for Jobs Service (Benchmark)'''

from service.tests.base import BaseTestCase
from service.api.utils import STATUS_CODE

class TestJOBS(BaseTestCase):
    ''' Test for post on Jobs Service '''

    def test_post_job_benchmark(self):
        ''' Ensure the user can create a benchmarking job '''

        data = {
            "settings": {
                "git": "git@git.eodc.eu:HQ-S2/benchmark-test-application.git",
                "ref": "master",
                "dir": ".",
                "start_cpu":"300m",
                "start_memory":"300Mi",
                "end_cpu":"2",
                "end_memory":"2Gi"
            }
        }

        response, data = self.send_post("/jobs/benchmark", data=data)

        self.assertEqual(response.status_code, 201)
        self.assertIn("Job sucessfully created!", data["message"])
        self.assertIn(STATUS_CODE[201], data["status"])

    def test_post_no_payload(self):
        ''' Ensure that an error is thrown if no payload is delivered '''

        response, data = self.send_post("/benchmark", data=None)

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid payload.", data["message"])
        self.assertIn(STATUS_CODE[400], data["status"])
