''' A job object represents an executable process chain '''

import uuid

class Job:
    def __init__(self, user_id, process_graph):
        self.id = uuid.uuid4()
        self.user_id = user_id
        self.process_graph = process_graph
        self.status = "initialized"
