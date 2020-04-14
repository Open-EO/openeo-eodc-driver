import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class JobStatus(enum.Enum):
    def __str__(self):
        return str(self.value)

    created = "created"  # JobStatus should never be queued -> does not exist for a dag in airflow
    queued = "queued"
    running = "running"
    canceled = "canceled"
    finished = "finished"
    error = "error"


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    process_graph_id = Column(String, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.created, nullable=False)
    status_updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    progress = Column(Integer, nullable=True)  # Should be filled persistently
    error = Column(JSON, nullable=True)  # store last error of job > needed for results response
    plan = Column(String, nullable=True)  # Implement plans in database/service
    budget = Column(Integer, nullable=True)
    current_costs = Column(Integer, nullable=True)
    logs = Column(String)
    metrics = Column(JSON)
    dag_filename = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
