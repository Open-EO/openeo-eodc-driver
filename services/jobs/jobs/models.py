from sqlalchemy import Column, Integer, String, Boolean, TEXT, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from uuid import uuid4

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    process_graph_id = Column(String, nullable=False)
    output = Column(JSON, default={"format": "GTiff"})    # Integrate output formats in table at data/volume service
    plan = Column(String, default="free")   # Implement plans in database/service
    budget = Column(Integer, default=0)
    current_costs = Column(Integer, default=0, nullable=False)
    status = Column(String, default="submitted", nullable=False)
    logs = Column(String, default={})
    metrics = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, user_id: str, process_graph_id: str, title: str=None, description: str=None, output: dict=None,
                 plan: str=None, budget: int=None):
        self.id = "jb-" + str(uuid4())
        self.user_id = user_id
        self.process_graph_id = process_graph_id
        if title: self.title = title
        if description: self.description = description
        if output: self.output = output
        if plan: self.plan = plan
        if budget: self.budget = budget
