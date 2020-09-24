"""This domain module provides the database model for the jobs database including auxiliary data structures."""
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
    """The job was submitted to be backend and stored there."""
    queued = "queued"  # JobStatus should never be queued -> does not exist for a dag in airflow
    """The user wants to start processing, but processing can not start instantly - does not exists on our backend."""
    running = "running"
    """The processing started and is now running."""
    canceled = "canceled"
    """The user stopped the processing while running - intermediate results are available for download."""
    finished = "finished"
    """The job finished successfully and the results are ready for download."""
    error = "error"
    """While running the job an error occurred."""


class Job(Base):
    """Job table definition."""

    __tablename__ = 'jobs'

    id = Column(String, primary_key=True)  # noqa A003
    """Unique string identifier of a job."""
    user_id = Column(String, nullable=False)
    """The id of the user own the job as a string."""
    title = Column(String, nullable=True)
    """A short description to easily distinguish entities."""
    description = Column(String, nullable=True)
    """Detailed multi-line description to explain the entity."""
    process_graph_id = Column(String, nullable=False)
    """Foreign key (string) to the corresponding process graph stored in the ProcessGraphDB."""
    status = Column(Enum(JobStatus), default=JobStatus.created, nullable=False)
    """The current status of the job as enum."""
    status_updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    """The UTC datetime of the last job 'status' update."""
    progress = Column(Integer, nullable=True)  # Should be filled persistently
    """Indicates the process of a running batch job in percent."""
    error = Column(JSON, nullable=True)  # store last error of job > needed for results response
    """Last error which occurred running the job as JSON."""
    plan = Column(String, nullable=True)  # Implement plans in database/service
    """The job plan."""
    budget = Column(Integer, nullable=True)
    """Maximum amount of costs the request is allowed to produce in cent."""
    current_costs = Column(Integer, nullable=True)
    """The current costs of the job in cent."""
    logs = Column(String)
    """Already produced logs - currently not filled."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    """UTC datetime the job was created."""
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    """UTC datetime any column of this job was last updated."""
