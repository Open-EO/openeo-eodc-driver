from os import environ
from sqlalchemy import Column, Integer, String, Boolean, TEXT, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Process(Base):
    __tablename__ = 'processes'

    process_id = Column(String, primary_key=True, nullable=False)
    user_id = Column(String, unique=True, nullable=False)
    description = Column(TEXT, nullable=False)
    process_type = Column(String, nullable=False)
    link = Column(String, nullable=True)
    args = Column(JSON, nullable=True)
    git_uri = Column(String, nullable=True)
    git_ref = Column(String, nullable=True)
    git_dir = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, process_id, user_id, description, process_type, link="", args={}, git_uri="", git_ref="", git_dir=""):
        self.process_id = process_id
        self.user_id = user_id
        self.description = description
        self.process_type = process_type
        self.link = link
        self.args = args
        self.git_uri = git_uri
        self.git_ref = git_ref
        self.git_dir = git_dir
