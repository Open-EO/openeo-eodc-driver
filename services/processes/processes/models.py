""" Models """
# TODO: Further normalize models

from sqlalchemy import Column, Integer, String, Boolean, TEXT, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from uuid import uuid4

Base = declarative_base()


class ProcessGraph(Base):
    """ Base model for a process graph. """

    __tablename__ = 'process_graphs'

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    title = Column(String, nullable=True)
    description = Column(TEXT, nullable=True)
    process_graph = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, user_id: str, process_graph: dict, title: str=None, description: str=None):

        self.id = "pg-" + str(uuid4())
        self.user_id = user_id
        self.process_graph = process_graph
        if title:
            self.title = title
        if description:
            self.description = description

    def update(self, process_graph: dict=None, title: str=None, description: str=None):
        if process_graph:
            self.process_graph = process_graph
        if title:
            self.title = title
        if description:
            self.description = description
