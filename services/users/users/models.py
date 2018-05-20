from sqlalchemy import Column, Integer, String, Boolean, TEXT, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(String, unique=True, nullable=False)
    password    = Column(String, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    active      = Column(Boolean, default=False, nullable=False)
    project     = Column(String, nullable=False)
    sa_token    = Column(TEXT, nullable=False)
    admin       = Column(Boolean, default=False, nullable=False)

    def __init__(self, user_id, password, project, sa_token):
        self.user_id = user_id
        self.password = password
        self.project = project
        self.sa_token = sa_token
