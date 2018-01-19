import datetime
from service import db
from sqlalchemy.dialects.postgresql import JSON


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer, nullable=False)
    settings = db.Column(db.String(512), nullable=False)
    status = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    result = db.Column(JSON, nullable=True)

    def __init__(self, owner_id, settings, status="scheduled", created_at=datetime.datetime.utcnow(), result=None):
        self.owner_id = owner_id
        self.settings = settings
        self.status = status
        self.created_at = created_at
        self.result = result

    def __repr__(self):
        return '<id {}>'.format(self.id)
