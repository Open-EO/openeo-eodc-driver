''' Model of Process '''

from datetime import datetime
from service import DB

class Process(DB.Model):
    ''' Process Model '''

    __tablename__ = "processes"

    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    user_id = DB.Column(DB.Integer, nullable=False)
    process_id = DB.Column(DB.String(128), nullable=False)
    description = DB.Column(DB.String(512), nullable=False)
    git_uri = DB.Column(DB.String(128), nullable=True)
    git_ref = DB.Column(DB.String(128), nullable=True)
    git_dir = DB.Column(DB.String(128), nullable=True)
    process_type = DB.Column(DB.String(128), nullable=False)
    args = DB.Column(DB.JSON, nullable=True)
    created_at = DB.Column(DB.DateTime, nullable=False)

    def __init__(self, user_id, process_id, description, process_type, git_uri=None, git_ref=None, git_dir=None, args=args, created_at=datetime.utcnow()):
        self.user_id = user_id
        self.process_id = process_id
        self.description = description
        self.git_uri = git_uri
        self.git_ref = git_ref
        self.git_dir = git_dir
        self.process_type = process_type
        self.args = args
        self.created_at = created_at
    
    def get_description(self):
        ''' Short process description '''

        return {
            "process_id": self.process_id,
            "description": self.description
        }
    
    def get_small_dict(self):
        ''' Reduced view that hides sensitive information '''

        return {
            "process_id": self.process_id,
            "description": self.description,
            "args": self.args,
            "created_at": self.created_at
        }

    def get_dict(self):
        return {
            "user_id": self.user_id,
            "process_id": self.process_id,
            "description": self.description,
            "git_uri": self.git_uri,
            "git_ref": self.git_ref,
            "git_dir": self.git_dir,
            "process_type": self.process_type,
            "args": self.args,
            "created_at": self.created_at
        }
