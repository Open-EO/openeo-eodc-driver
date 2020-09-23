"""This domain module provides the database model for the jobs database."""
import enum
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Enum, Integer, JSON, String
from sqlalchemy.ext.declarative import declarative_base

Base: Any = declarative_base()


class JobStatus(enum.Enum):
    """Enumerator holding all states a job can be in."""

    def __str__(self) -> str:
        """Return the value as a string."""
        return str(self.value)

    created = "created"
    queued = "queued"  # JobStatus should never be queued -> does not exist for a dag in airflow
    running = "running"
    canceled = "canceled"
    finished = "finished"
    error = "error"


class Job(Base):
    """Job table definition."""

    __tablename__ = 'jobs'

    id = Column(String, primary_key=True)  # noqa A003
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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
