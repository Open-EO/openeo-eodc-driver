""" Models """
# TODO: Normalize model? -> Currently not possible because of variable dict names

from os import environ
from sqlalchemy import Column, Integer, String, Boolean, TEXT, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Process(Base):
    """ Base model for a process description. """

    __tablename__ = 'processes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    summary = Column(TEXT, nullable=True)
    description = Column(TEXT, nullable=False)
    parameters = Column(JSON, nullable=False)
    min_parameters = Column(Integer, nullable=True)
    returns = Column(JSON, nullable=False)
    deprecated = Column(Boolean, default=False)
    exceptions = Column(JSON, nullable=True)
    examples = Column(JSON, nullable=True)
    links = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


    def __init__(self, name, summary, description, parameters, min_parameters, 
                 returns, deprecated, exceptions, examples, links):
        self.name = name
        self.summary = summary
        self.description = description
        self.parameters = parameters
        self.min_parameters = min_parameters
        self.returns = returns
        self.deprecated = deprecated
        self.exceptions = exceptions
        self.examples = examples
        self.links = links


# class Process(Base):
#     __tablename__ = 'processes'

#     process_id = Column(String, primary_key=True, nullable=False)
#     user_id = Column(String, unique=True, nullable=False)
#     description = Column(TEXT, nullable=False)
#     process_type = Column(String, nullable=False)
#     link = Column(String, nullable=True)
#     args = Column(JSON, nullable=True)
#     git_uri = Column(String, nullable=True)
#     git_ref = Column(String, nullable=True)
#     git_dir = Column(String, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

#     def __init__(self, process_id, user_id, description, process_type, link="", args={}, git_uri="", git_ref="", git_dir=""):
#         self.process_id = process_id
#         self.user_id = user_id
#         self.description = description
#         self.process_type = process_type
#         self.link = link
#         self.args = args
#         self.git_uri = git_uri
#         self.git_ref = git_ref
#         self.git_dir = git_dir
