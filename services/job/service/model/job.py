''' Model of Job '''

from datetime import datetime
from service import DB

class Job(DB.Model):
    ''' Job Model '''

    __tablename__ = "jobs"

    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    user_id = DB.Column(DB.Integer, nullable=False)
    task = DB.Column(DB.JSON, nullable=True)
    status = DB.Column(DB.String(128), nullable=False)
    submitted = DB.Column(DB.DateTime, nullable=False)
    last_update = DB.Column(DB.DateTime, nullable=False)
    consumed_credits = DB.Column(DB.Float, nullable=False)

    def __init__(self, user_id, task, status="submitted", submitted=datetime.utcnow(), last_update=datetime.utcnow(), consumed_credits=0):
        self.user_id = user_id
        self.task = task
        self.status = status
        self.submitted = submitted
        self.last_update = last_update
        self.consumed_credits = consumed_credits

    def get_dict(self):
        return {
            "job_id": self.id,
            "user_id": self.user_id,
            "task": self.task,
            "status": self.status,
            "submitted": self.submitted,
            "updated": self.last_update,
            "consumed_credits": self.consumed_credits
        }

    def get_small_dict(self):
        return {
            "job_id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "submitted": self.submitted,
            "updated": self.last_update,
            "consumed_credits": self.consumed_credits
        }

