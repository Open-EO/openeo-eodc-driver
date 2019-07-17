from sqlalchemy import Column, Integer, String, Boolean, TEXT, DateTime, ForeignKey, JSON, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from uuid import uuid4
import enum
import json

Base = declarative_base()


class JobStatus(enum.Enum):
    def __str__(self):
        return str(self.value)
    submitted = "submitted"
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
    status = Column(Enum(JobStatus), default=JobStatus.submitted, nullable=False)
    progress = Column(Integer, nullable=True)
    error = Column(JSON, nullable=True)
    plan = Column(String, default="free", nullable=True)  # Implement plans in database/service
    budget = Column(Float, default=0, nullable=True)
    current_costs = Column(Float, default=0, nullable=True)
    logs = Column(String, default=json.dumps({}))
    metrics = Column(JSON, default=json.dumps({}))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, user_id: str, process_graph_id: str, title: str=None, description: str=None, plan: str=None,
                 budget: int=None):
        self.id = "jb-" + str(uuid4())
        self.user_id = user_id
        self.process_graph_id = process_graph_id
        if title:
            self.title = title
        if description:
            self.description = description
        if plan:
            self.plan = plan
        if budget:
            self.budget = budget

    def update(self, process_graph_id: str=None, title: str=None, description: str=None, plan: str=None,
               budget: int=None):
        if process_graph_id:
            self.process_graph_id = process_graph_id
        if title:
            self.title = title
        if description:
            self.description = description
        if plan:
            self.plan = plan
        if budget:
            self.budget = budget
