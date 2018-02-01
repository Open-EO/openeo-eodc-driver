''' ProcessGraph Class '''

class ProcessGraph:
    ''' A ProcessGraph parses the graph from the input payload and contains the executable process nodes. '''

    def __init__(self, payload):
        self.validate_payload(payload)

    def validate_payload(self):
        