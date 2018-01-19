import json
from service.tests.base import BaseTestCase
from service.model.job import Job
from service import db


class TestJobModel(BaseTestCase):
    def test_add_job(self):
        ''' Ensure that the Job model is correct '''

        settings = {
            "url": "git@git.eodc.eu:HQ-S2/benchmark-test-application.git",
            "ref": "master",
            "dir": ".",
            "limit_cpu":"300m",
            "limit_memory":"300Mi",
            "requests_cpu":"300m",
            "requests_memory":"300Mi"
        }

        job = Job(1, json.dumps(settings))

        db.session.add(job)
        db.session.commit()

        self.assertTrue(job.id)
        self.assertEqual(job.status, "scheduled")
        self.assertEqual(job.result, None)
        self.assertTrue(job.settings)
        self.assertTrue(job.created_at)
