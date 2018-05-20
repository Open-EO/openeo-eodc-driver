from sqlalchemy import Column, Integer, String, Boolean, TEXT, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    tasks = relationship("Task", back_populates="job")
    status = Column(String, default="submitted", nullable=False)
    credits = Column(Integer, default=0, nullable=False)
    process_graph = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)

    def __init__(self, user_id, process_graph, output):
        self.user_id = user_id
        self.process_graph = process_graph
        self.output = output


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    job = relationship("Job", back_populates="tasks")
    process_id = Column(String, nullable=False)
    seq_num = Column(Integer, nullable=False)
    # next = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    args = Column(JSON, nullable=True)
    status = Column(String, default="initialized", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)

    def __init__(self, job_id, process_id, seq_num, args): #, next
        self.job_id = job_id
        self.process_id = process_id
        self.seq_num = seq_num
        self.args = args
        # self.next = next
