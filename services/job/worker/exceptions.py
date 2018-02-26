''' Worker Exceptions '''

class TemplateError(Exception):
    ''' Template Exception raises if the template could not be parsed or excecuted. '''
    def __init__(self, msg=None):
        if not msg:
            msg = "Error while parsing templates."
        super(TemplateError, self).__init__(msg)

class ProcessingError(Exception):
    ''' Processing Exception raises at runtime if process could not be executed. '''
    
    def __init__(self, msg=None):
        if not msg:
            msg = "Error while executing ProcessingGraph."
        super(ProcessingError, self).__init__(msg)

