""" Models """
# TODO: Further normalize models

from os import environ
from sqlalchemy import Column, Integer, String, Boolean, TEXT, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from uuid import uuid4

Base = declarative_base()

class Process(Base):
    """ Base model for a process description. """

    __tablename__ = 'processes'

    id = Column(String, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    name = Column(String, nullable=False, unique=True)
    summary = Column(TEXT, nullable=True)
    description = Column(TEXT, nullable=False)
    parameters = relationship('Parameter', backref='process')
    min_parameters = Column(Integer, nullable=True)
    returns = Column(JSON, nullable=False)
    deprecated = Column(Boolean, default=False)
    exceptions = Column(JSON, nullable=True)
    examples = Column(JSON, nullable=True)
    links = Column(JSON, nullable=True)
    p_type = Column(String, default="operation")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


    def __init__(self, user_id: str, name: str, description: str, returns: dict, summary: str=None,
                 min_parameters: int=None, deprecated: bool=None, exceptions: dict=None, 
                 examples: dict=None, links: dict=None, p_type: dict=None):
        
        self.id = "pc-" + str(uuid4())
        self.user_id = user_id
        self.name = name
        self.description = description
        self.returns = returns
        if summary: self.summary = summary
        if min_parameters: self.min_parameters = min_parameters
        if deprecated: self.deprecated = deprecated
        if exceptions: self.exceptions = exceptions
        if examples: self.examples = examples
        if links: self.links = links
        if p_type: self.p_type = p_type


class Parameter(Base):
    """ Base model for a process graph parameters. """

    __tablename__ = 'parameters'

    id = Column(String, primary_key=True, autoincrement=True)
    process_id = Column(String, ForeignKey('processes.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(TEXT, nullable=False)
    required = Column(Boolean, default=False)
    deprecated = Column(Boolean, default=False)
    mime_type = Column(String, nullable=True)
    schema = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, process_id: str, name: str, description: str, schema: dict,
                 required: bool=None, deprecated: bool=None,mime_type: str=None):

        self.id = "pa-" + str(uuid4())
        self.process_id = process_id
        self.name = name
        self.description = description
        self.required = required
        self.deprecated = deprecated
        self.schema = schema
        if required: self.required = required
        if deprecated: self.deprecated = deprecated
        if mime_type: self.mime_type = mime_type


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
