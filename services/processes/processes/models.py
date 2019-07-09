""" Models """
# TODO: Further normalize models

from sqlalchemy import Column, Integer, String, Boolean, TEXT, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
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
    nodes = relationship('ProcessNode', backref='process_graph')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, user_id: str, process_graph: dict, title: str=None, description: str=None):

        self.id = "pg-" + str(uuid4())
        self.user_id = user_id
        self.process_graph = process_graph
        if title: self.title = title
        if description: self.description = description


class ProcessNode(Base):
    """ Base model for a node of a process graph. """

    __tablename__ = 'process_nodes'

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    seq_num = Column(Integer, nullable=True)
    process_graph_id = Column(String, ForeignKey("process_graphs.id"), nullable=False)
    process_id = Column(String, nullable=False)
    imagery_id = Column(String, ForeignKey("process_nodes.id"), nullable=True)
    imagery = relationship('ProcessNode', remote_side=[id])
    args = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, user_id: str, seq_num: int, process_graph_id: str, process_id: str,
                 imagery_id: str=None, args: dict=None):

        self.id = "pn-" + str(uuid4())
        self.user_id = user_id
        self.seq_num = seq_num
        self.process_graph_id = process_graph_id
        self.process_id = process_id
        if imagery_id: self.imagery_id = imagery_id
        if args: self.args = args
